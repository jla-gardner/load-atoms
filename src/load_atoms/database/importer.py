from __future__ import annotations

import shutil
import warnings
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator

import ase.io
from ase import Atoms
from typing_extensions import override

from load_atoms.atoms_dataset import (
    AtomsDataset,
    get_file_extension_and_dataset_class,
)
from load_atoms.database.database_entry import DatabaseEntry
from load_atoms.database.internet import download as _download
from load_atoms.progress import Progress
from load_atoms.utils import debug_mode, matches_checksum, testing

BASE_GITHUB_URL = "https://github.com/jla-gardner/load-atoms/raw/main/database"


@dataclass
class FileDownload:
    url: str
    expected_hash: str
    local_name: str = None  # type: ignore

    def __post_init__(self):
        if self.local_name is None:
            self.local_name = Path(self.url).name


def download_all(files: list[FileDownload], tmp_dir: Path, progress: Progress):
    """
    Download all files and verify their checksums.

    Parameters
    ----------
    files
        A list of FileDownloads
    tmp_dir
        The directory where the files should be saved.
    progress
        A Progress object to track the download progress.
    """

    # 1. download any missing files
    for file in files:
        local_path = tmp_dir / file.local_name
        if not local_path.exists():
            _download(file.url, local_path, progress)

    # 2. verify the hashes of all files
    for file in files:
        local_path = tmp_dir / file.local_name
        if not matches_checksum(local_path, file.expected_hash):
            warnings.warn(
                f"Checksum mismatch for file: {local_path}",
                stacklevel=2,
            )


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

    # TODO: add expected format to the init

    def __init__(
        self,
        files_to_download: list[FileDownload],
        cleanup: bool = True,
    ):
        self.files_to_download = files_to_download
        self.cleanup = cleanup

    @abstractmethod
    def get_structures(
        self,
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

    def save_and_load_dataset(
        self,
        temp_dir: Path,
        data_file_stem: Path,
        database_entry: DatabaseEntry,
        progress: Progress,
    ) -> AtomsDataset:
        """Get the dataset for this importer.

        Parameters
        ----------
        temp_dir
            The temporary directory to download the dataset to.
        data_file_stem
            The file path stem (i.e. the file name without the extension) to
            save the final dataset.
        database_entry
            The database entry for the dataset.
        progress
            A :class:`Progress` object to track the download progress.
        """

        (extension, dataset_class) = get_file_extension_and_dataset_class(
            database_entry.format
        )

        data_file = data_file_stem.with_suffix(extension)

        # ensure file structure exists
        temp_dir.mkdir(parents=True, exist_ok=True)
        data_file_stem.parent.mkdir(parents=True, exist_ok=True)
        if data_file.exists():
            raise FileExistsError(f"Dataset already exists at {data_file}")

        # download all the required files
        download_all(self.files_to_download, temp_dir, progress)

        # save and load the dataset
        def iterator():
            for structure in self.get_structures(temp_dir, progress=progress):
                structure.calc = None
                yield structure

        try:
            dataset_class.save(data_file, iterator(), database_entry)
            return dataset_class.load(data_file)

        finally:
            if self.cleanup and not debug_mode() and not testing():
                shutil.rmtree(temp_dir)


class SingleFileImporter(BaseImporter):
    def __init__(self, url: str, hash: str):
        super().__init__(
            [FileDownload(url, hash)],
            cleanup=False,
        )

    @override
    def get_structures(
        self, tmp_dir: Path, progress: Progress
    ) -> Iterator[Atoms]:
        file_path = tmp_dir / Path(self.files_to_download[0].local_name)
        with progress.new_task(
            f"Reading {file_path.resolve()}",
            transient=True,
        ):
            for atoms in self._read_file(file_path):
                yield self.process_atoms(atoms)

    def process_atoms(self, atoms: Atoms) -> Atoms:
        return atoms

    def _read_file(self, file_path: Path) -> Iterator[Atoms]:
        yield from ase.io.iread(file_path, index=":")


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
