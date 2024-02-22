"""
The :code:`backend` module is responsible for down/loading datasets by name, 
storing them locally, and serving them to :code:`load-atoms` via the
:func:`~load_atoms.load_dataset` function.
"""

from __future__ import annotations

import pickle
import shutil
import warnings
from pathlib import Path

from ase import Atoms

from load_atoms.database.database_entry import DatabaseEntry, FileInformation
from load_atoms.database.internet import download, download_all
from load_atoms.progress import Progress
from load_atoms.utils import UnknownDatasetException, matches_checksum


def load_structures(name: str, root: Path) -> tuple[list[Atoms], DatabaseEntry]:
    """
    Load the structures comprising the dataset with the given id from the
    given path.

    If these structures are not currently present, download and process
    them first.

    Parameters
    ----------
    name
        The id of the dataset to load.
    root
        The root folder to save the structures to.
    """
    with Progress(f"Loading {name}") as progress:
        result = _load_structures(name, root, progress)
        progress._live.refresh()
    return result


def _load_structures(name, root, progress):
    entry_path = root / name / f"{name}.yaml"
    structures_path = root / name / f"{name}.pkl"
    temp_path = root / name / "temp"

    entry_path.parent.mkdir(parents=True, exist_ok=True)

    # we first need to get the DatabaseEntry for the dataset
    if not (entry_path).exists():
        try:
            download(DatabaseEntry.remote_url_for(name), entry_path)
        except Exception as e:
            raise UnknownDatasetException(name) from e
    entry = DatabaseEntry.from_yaml_file(entry_path)

    # try to load the structures from disk
    if structures_path.exists():
        with progress.new_task("Reading from disk"), open(
            structures_path, "rb"
        ) as f:
            structures = pickle.load(f)
        return structures, entry

    # else, download and process the dataset

    # 1. download the dataset files
    temp_path.mkdir(parents=True, exist_ok=True)

    # the following lines add no performance overhead, but are useful for
    # when debugging the adding of new datasets
    existing_files: list[str] = [f.name for f in temp_path.iterdir()]
    missing_files: list[FileInformation] = [
        file for file in entry.files if file.name not in existing_files
    ]

    download_all(
        [file.url for file in missing_files],
        [temp_path / file.name for file in missing_files],
    )

    # 2. validate the downloaded files
    for file_info in entry.files:
        file = temp_path / file_info.name
        if not matches_checksum(file, file_info.hash):
            warnings.warn(
                f"Checksum of {file_info.name} does not match the "
                "expected value. This means that the downloaded dataset "
                "may be corrupted.",
                stacklevel=2,
            )

    # 3. process the downloaded files into structures
    structures = entry.processing(temp_path)
    # remove annoying default calculators
    for s in structures:
        s.calc = None

    # 4. save the structures to disk
    with progress.new_task("Caching to disk"), open(structures_path, "wb") as f:
        pickle.dump(structures, f)

    # 5. clean up the download directory
    # if debugging, comment out this line to inspect the downloaded files
    # rather than deleting them

    with progress.new_task("Cleaning up", transient=True):
        shutil.rmtree(temp_path)

    return structures, entry
