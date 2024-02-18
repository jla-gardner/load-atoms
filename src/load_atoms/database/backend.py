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
from load_atoms.database.processing import parse_steps
from load_atoms.utils import UnknownDatasetException, matches_checksum


def load_structures(
    dataset_id: str, root: Path
) -> tuple[list[Atoms], DatabaseEntry]:
    """
    Load the structures comprising the dataset with the given id from the
    given path.

    If these structures are not currently present, download and process
    them first.

    Parameters
    ----------
    dataset_id
        The id of the dataset to load.
    root
        The root folder to save the structures to.
    """

    # we first need to get the DatabaseEntry for the dataset
    entry_path = root / dataset_id / f"{dataset_id}.yaml"
    if not (entry_path).exists():
        try:
            download(DatabaseEntry.remote_url_for(dataset_id), root)
        except Exception as e:
            raise UnknownDatasetException(dataset_id) from e
    entry = DatabaseEntry.from_yaml_file(entry_path)

    # now we can get the structures
    structures_path = root / dataset_id / f"{dataset_id}.xyz"
    if structures_path.exists():
        # TODO: implement fast reading with progress bar
        return read(structures_path, index=":"), entry  # type: ignore

    # if the structures don't exist, we need to download files, validate them,
    # process them into structures, and save the structures to disk

    # 1. download the dataset files
    remote_file_locations = entry.remote_file_locations()
    download_dir = (
        root / dataset_id / "temp"
    )  # TODO use actual temp at some point : read up about this
    download_all(list(remote_file_locations.values()), download_dir)

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
    processing_function = parse_steps(entry.processing)
    structures = processing_function(download_dir)

    # 4. save the structures to disk
    structures_path.parent.mkdir(parents=True, exist_ok=True)
    write(structures_path, structures)

    return structures, entry
