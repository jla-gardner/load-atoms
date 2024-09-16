"""
The :code:`backend` module is responsible for down/loading datasets by name, 
storing them locally, and serving them to :code:`load-atoms` via the
:func:`~load_atoms.load_dataset` function.
"""

from __future__ import annotations

import shutil
import tempfile
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Iterator

import ase.io
from ase import Atoms
from typing_extensions import override

from load_atoms.atoms_dataset import (
    AtomsDataset,
    get_file_extension_and_dataset_class,
)
from load_atoms.database.database_entry import (
    LICENSE_URLS,
    DatabaseEntry,
)
from load_atoms.database.internet import FileDownload, download, download_all
from load_atoms.progress import Progress, get_progress_for_dataset
from load_atoms.utils import (
    UnknownDatasetException,
    debug_mode,
    frontend_url,
    testing,
)

BASE_GITHUB_URL = "https://github.com/jla-gardner/load-atoms/raw/main/database"


def load_dataset_by_id(dataset_id: str, root: Path) -> AtomsDataset:
    """
    Load the :class:`AtomsDataset` and corresponding :class:`DatabaseEntry` for
    the given dataset id, saving the dataset to the given ``root`` directory.

    Parameters
    ----------
    name
        The id of the dataset to load.
    root
        The root folder to save the structures to.
    """

    # prepare local paths
    yaml_file_path = root / "database-entries" / f"{dataset_id}.yaml"
    yaml_file_path.parent.mkdir(parents=True, exist_ok=True)

    with get_progress_for_dataset(dataset_id) as progress:
        # down/load the dabase entry for the dataset
        database_entry = get_database_entry(
            dataset_id, yaml_file_path, progress
        )

        # get the file extension and dataset class for the dataset
        extension, dataset_class = get_file_extension_and_dataset_class(
            database_entry.format
        )
        data_file_path = root / f"{dataset_id}.{extension}"

        # if the dataset already exists, load it from disk
        if data_file_path.exists():
            with progress.new_task("Reading from disk"):
                dataset = dataset_class.load(data_file_path)

        # otherwise, use the importer to get the structures
        else:
            # 1. get the Importer class from a suitably down/loaded file
            importer_type: type[BaseImporter] = get_importer_type(
                dataset_id, progress
            )

            # 2. download the files to an appropriate directory
            download_dir_name = importer_type.permanent_download_dirname()
            use_tmp_dir = (
                download_dir_name is None and not debug_mode() and not testing()
            )
            if use_tmp_dir:
                download_dir = Path(tempfile.mkdtemp())
            else:
                download_dir = (
                    root / "raw-downloads" / (download_dir_name or dataset_id)
                )
            download_all(
                importer_type.files_to_download(), download_dir, progress
            )

            # 3. use the importer to get the structures (removing annoying calc)
            def iterator():
                for structure in importer_type.get_structures(
                    download_dir, progress
                ):
                    structure.calc = None
                    yield structure

            try:
                dataset_class.save(data_file_path, iterator(), database_entry)

            except Exception as e:
                # remove the partially created dataset
                if data_file_path.exists():
                    if data_file_path.is_dir():
                        shutil.rmtree(data_file_path)
                    else:
                        data_file_path.unlink()

                raise ValueError(
                    "Failed to import dataset: please report an issue at "
                    "https://github.com/jla-gardner/load-atoms/issues if you "
                    "think this is a bug."
                ) from e

            dataset = dataset_class.load(data_file_path)

            # 4. clean up the temporary directory if necessary
            if use_tmp_dir:
                shutil.rmtree(download_dir)

        # add the usage information to the progress bar
        log_usage_information(database_entry, progress)

        progress.refresh()

    return dataset


class BaseImporter(ABC):
    """
    Base class to inherit from to create new, dataset-specific importers.

    Parameters
    ----------
    files_to_download
        A list of :class:`FileDownload` s
    tmp_dirname
        The name of the temporary directory to download the files to.
    cleanup
        Whether to clean up the temporary directory after processing.
    """

    @classmethod
    def files_to_download(cls) -> list[FileDownload]:
        return []

    @classmethod
    @abstractmethod
    def get_structures(
        cls,
        tmp_dir: Path,
        progress: Progress,
    ) -> Iterator[Atoms]:
        """
        Iterate over :class:`ase.Atoms` objects. All files passed
        to the base class will have already been downloaded
        and verified when this is called.

        Parameters
        ----------
        tmp_dir
            The temporary directory where downloaded files are stored.

        Yields
        ------
        Atoms
            An iterator of ASE Atoms objects processed from the downloaded files
        """

    @classmethod
    def permanent_download_dirname(cls) -> str | None:
        """
        Get a path to the directory where the files should be saved.
        If ``None`` (the default), is returned, the files will be downloaded
        to a temporary directory, and removed after the dataset is imported.
        """
        return None


class SingleFileImporter(BaseImporter):
    @classmethod
    @abstractmethod
    def file_to_download(cls) -> FileDownload:
        ...

    @classmethod
    def files_to_download(cls) -> list[FileDownload]:
        return [cls.file_to_download()]

    @override
    @classmethod
    def get_structures(
        cls, tmp_dir: Path, progress: Progress
    ) -> Iterator[Atoms]:
        file_path = tmp_dir / Path(cls.files_to_download()[0].local_name)
        with progress.new_task(f"Reading {file_path.resolve()}"):
            for atoms in cls._read_file(file_path):
                yield cls.process_atoms(atoms)

    @classmethod
    def process_atoms(cls, atoms: Atoms) -> Atoms:
        return atoms

    @classmethod
    def _read_file(cls, file_path: Path) -> Iterator[Atoms]:
        yield from ase.io.iread(file_path, index=":")


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~ HELPERS ~~~~~~~~~~~~~~~~~~~~~~~~~~~ #


def get_database_entry(
    dataset_id: str,
    yaml_file_path: Path,
    progress: Progress,
) -> DatabaseEntry:
    from load_atoms import __version__ as load_atoms_version

    if not yaml_file_path.exists():
        try:
            download(
                DatabaseEntry.remote_url_for_yaml(dataset_id),
                yaml_file_path,
                progress,
            )
        except Exception as e:
            raise UnknownDatasetException(dataset_id) from e

    db_entry = DatabaseEntry.from_yaml_file(yaml_file_path)

    if (
        db_entry.minimum_load_atoms_version is not None
        and db_entry.minimum_load_atoms_version > load_atoms_version
    ):
        raise Exception(
            f"Dataset {dataset_id} requires load-atoms version "
            f">={db_entry.minimum_load_atoms_version} "
            f"(current version: {load_atoms_version}). "
            "Please upgrade load-atoms to load this dataset "
            "(e.g. `pip install --upgrade load-atoms`)."
        )

    return db_entry


def get_importer_type(
    dataset_id: str,
    progress: Progress,
) -> type[BaseImporter]:
    importer_name = DatabaseEntry.importer_file_stem(dataset_id)
    expected_importer_path = (
        Path(__file__).parent / "importers" / f"{importer_name}.py"
    )

    if not expected_importer_path.exists():
        try:
            download(
                DatabaseEntry.remote_url_for_importer(dataset_id),
                expected_importer_path,
                progress,
            )
        except Exception as e:
            # couldn't download the importer:
            raise UnknownDatasetException(dataset_id) from e

    try:
        return __import__(
            f"load_atoms.database.importers.{importer_name}",
            fromlist=["Importer"],
        ).Importer

    except Exception as e:
        raise Exception(
            f"Unable to load dataset {dataset_id} due to a problem loading "
            "the dataset's importer file. Please try updating load-atoms:\n"
            "  pip install --upgrade load-atoms\n"
            "If the problem persists, please report an issue at:\n"
            "  https://github.com/jla-gardner/load-atoms/issues"
        ) from e


def log_usage_information(info: DatabaseEntry, progress: Progress):
    progress.add_text("\n")

    name = f"[bold]{info.name}[/bold]"
    if info.license is not None:
        style = f"dodger_blue2 link={LICENSE_URLS[info.license]} underline"
        progress.add_text(
            f"The {name} dataset is covered by the "
            f"[{style}]{info.license}[/] license."
        )
    if info.citation is not None:
        progress.add_text(
            f"Please cite the {name} dataset " "if you use it in your work."
        )
    progress.add_text(f"For more information about the {name} dataset, visit:")
    url = frontend_url(info)
    url_style = f"dodger_blue2 underline link={url}"
    progress.add_text(f"[{url_style}]load-atoms/{info.name}")


def unzip_file(file_path: Path, progress: Progress) -> Path:
    """Unzip a file and return the path to the extracted directory.

    Parameters
    ----------
    file_path
        The path to the file to unzip.
    progress
        A :class:`Progress` object to track the unzip progress.
    """

    extract_to = file_path.parent / f"{file_path.name}-extracted"
    if not extract_to.exists():
        with progress.new_task(
            f"Unzipping {file_path.resolve()}",
        ):
            shutil.unpack_archive(file_path, extract_dir=extract_to)
    return extract_to


def rename(atoms: Atoms, mapping: dict[str, str]) -> Atoms:
    """Rename the properties of an Atoms object."""

    for old_name, new_name in mapping.items():
        if old_name in atoms.arrays:
            atoms.arrays[new_name] = atoms.arrays.pop(old_name)
        elif old_name in atoms.info:
            atoms.info[new_name] = atoms.info.pop(old_name)
    return atoms
