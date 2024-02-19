"""
The :code:`backend` module is responsible for down/loading datasets by name, 
storing them locally, and serving them to :code:`load-atoms` via the
:func:`~load_atoms.load_dataset` function.
"""

from __future__ import annotations

import warnings
from pathlib import Path

from ase import Atoms
from ase.io import read, write

from load_atoms.database import DatabaseEntry
from load_atoms.database.internet import download, download_all
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

    # we first need to get the DatabaseEntry for the dataset
    entry_path = root / name / f"{name}.yaml"
    if not (entry_path).exists():
        try:
            download(DatabaseEntry.remote_url_for(name), entry_path)
        except Exception as e:
            raise UnknownDatasetException(name) from e
    entry = DatabaseEntry.from_yaml_file(entry_path)

    # now we can get the structures
    structures_path = root / name / f"{name}.xyz"
    if structures_path.exists():
        # TODO: implement fast reading with progress bar
        return read(structures_path, index=":"), entry  # type: ignore

    # if the structures don't exist, we need to download files, validate them,
    # process them into structures, and save the structures to disk

    # 1. download the dataset files
    download_dir = root / name / "temp"
    # TODO use actual temp at some point : read up about this
    download_dir.mkdir(parents=True, exist_ok=True)
    existing_files = (f.name for f in download_dir.iterdir())
    missing_files = set(entry.files) - set(existing_files)
    download_all(
        [entry.remote_location(file) for file in missing_files],
        download_dir,
    )

    # 2. validate the downloaded files
    for file_name, hash in entry.files.items():
        file = download_dir / file_name
        if not matches_checksum(file, hash):
            warnings.warn(
                f"Checksum of {file_name} does not match the "
                "expected value. This means that the downloaded dataset "
                "may be corrupted.",
                stacklevel=2,
            )

    # 3. process the downloaded files into structures
    structures = entry.process(download_dir)

    # 4. save the structures to disk
    structures_path.parent.mkdir(parents=True, exist_ok=True)
    for s in structures:
        s.calc = None
    write(structures_path, structures)
    # TODO: implement fast writing with progress bar, and removal of calculators

    return structures, entry
