"""
The :code:`backend` module is responsible for down/loading datasets by name, 
storing them locally, and serving them to :code:`load-atoms` via the
:func:`~load_atoms.load_dataset` function.
"""

from __future__ import annotations

from pathlib import Path

from load_atoms.atoms_dataset import AtomsDataset
from load_atoms.database.database_entry import (
    LICENSE_URLS,
    DatabaseEntry,
)
from load_atoms.database.internet import download
from load_atoms.progress import Progress
from load_atoms.utils import UnknownDatasetException, frontend_url


def load_dataset(
    dataset_id: str,
    root: Path,
) -> AtomsDataset:
    """
    Load the :class:`AtomsDataset` and corresponding :class:`DatabaseEntry` for
    the given dataset id, using the given ``root`` directory to cache data.

    Parameters
    ----------
    name
        The id of the dataset to load.
    root
        The root folder to save the structures to.
    """

    # prepare local paths
    yaml_file_path = root / dataset_id / f"{dataset_id}.yaml"
    data_file_path = root / dataset_id / f"{dataset_id}.pkl"
    yaml_file_path.parent.mkdir(parents=True, exist_ok=True)

    with Progress(f"[bold]{dataset_id}") as progress:
        database_entry = get_database_entry(
            dataset_id, yaml_file_path, progress
        )

        # load the structures from disk if they exist
        if data_file_path.exists():
            with progress.new_task("Reading from disk"):
                dataset = AtomsDataset.load(data_file_path)

        # otherwise, use the importer to get the structures
        else:
            dataset = import_dataset(dataset_id, root, progress, database_entry)

            # cache the structures to disk for future re-use
            with progress.new_task("Caching to disk"):
                dataset.save(data_file_path)

        log_usage_information(database_entry, progress)

        # refresh the progress bar to ensure the final message is displayed
        progress._live.refresh()

    return dataset


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


def import_dataset(
    dataset_id: str,
    root: Path,
    progress: Progress,
    database_entry: DatabaseEntry,
) -> AtomsDataset:
    from load_atoms.database.importer import BaseImporter

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

    # TODO: nice error messages?
    importer: BaseImporter = __import__(
        f"load_atoms.database.importers.{importer_name}",
        fromlist=["Importer"],
    ).Importer()

    return importer.get_dataset(
        root_dir=root / "raw-downloads",
        database_entry=database_entry,
        progress=progress,
    )


def log_usage_information(info: DatabaseEntry, progress: Progress):
    progress.log_below("\n")

    name = f"[bold]{info.name}[/bold]"
    if info.license is not None:
        style = f"dodger_blue2 link={LICENSE_URLS[info.license]} underline"
        progress.log_below(
            f"The {name} dataset is covered by the "
            f"[{style}]{info.license}[/] license."
        )
    if info.citation is not None:
        progress.log_below(
            f"Please cite the {name} dataset " "if you use it in your work."
        )
    progress.log_below(f"For more information about the {name} dataset, visit:")
    url = frontend_url(info)
    url_style = f"dodger_blue2 underline link={url}"
    progress.log_below(f"[{url_style}]load-atoms/{info.name}")
