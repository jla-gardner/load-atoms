"""
The backend is responsible for downloading the datasets when they 
are first loaded, and for loading these datasets into memory afterwards.
The access point for this behaviour is the `get_structures` function. 
"""

from pathlib import Path
from typing import List, Union

from ase import Atoms
from ase.io import read
from rich.progress import track

from load_atoms.checksums import generate_checksum
from load_atoms.database import DatasetDescription
from load_atoms.download import Download, download_all
from load_atoms.util import DEFAULT_DOWNLOAD_DIR


class CorruptionError(Exception):
    def __init__(self, path: Path):
        super().__init__(
            f"File {path} exists, but did not match the expected checksum. "
            "Have you changed this file? If so, "
            "lease move it to a different location, or delete it."
        )


def get_structures(
    dataset: DatasetDescription, root: Union[Path, str, None] = None
) -> List[Atoms]:
    """
    Get the structures associated with a dataset.
    """

    # if no root is specified, use the default download directory
    if root is None:
        root = DEFAULT_DOWNLOAD_DIR
    root = Path(root)

    # first, we download any missing files:
    missing_files = [file for file in dataset.files if not (root / file).exists()]
    if missing_files:
        tasks = [
            Download(url=dataset.url_root + file, save_to=root / file)
            for file in missing_files
        ]
        download_all(tasks)

    # now, we can load the structures from the files
    all_structures = []

    # if there are lots of files, show a progress bar
    if len(dataset.files) > 3:
        iterator = track(
            dataset.files.items(),
            description="Loading files from disk",
            total=len(dataset.files),
        )
    else:
        iterator = dataset.files.items()

    for file, hash in iterator:
        local_path = root / file
        check_file_contents(local_path, hash)
        structures = read(local_path, index=":")
        all_structures.extend(structures)

    return all_structures


def check_file_contents(local_path: Path, expected_file_hash: str):
    file_hash = generate_checksum(local_path)
    if expected_file_hash != file_hash:
        raise CorruptionError(local_path)
