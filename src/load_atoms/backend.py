"""
The backend is responsible for downloading the datasets when they 
are first loaded, and for loading these datasets into memory, via
the `get_structures` function. 
"""

import math
from pathlib import Path
from typing import List

import requests
from ase import Atoms
from ase.io import read

from load_atoms.checksums import generate_checksum
from load_atoms.database import DatasetDescription
from load_atoms.util import BASE_REMOTE_URL, DEFAULT_DOWNLOAD_DIR, progress_bar


def get_structures(dataset: DatasetDescription, root: Path = None) -> List[Atoms]:
    """
    Get the structures associated with a dataset.
    """

    if root is None:
        root = DEFAULT_DOWNLOAD_DIR
    else:
        root = Path(root)

    all_structures = []

    for file, hash in dataset.files.items():
        local_path = root / file
        download_structures(
            BASE_REMOTE_URL + file,
            local_path,
            hash,
            f"Downloading {file}",
        )
        try:
            structures = read(local_path, index=":")
        except:
            # we can't read the ase file, so delete it and ask to try again
            local_path.unlink()
            raise ValueError(
                f"Could not read {local_path}.\n"
                "This is probably due to a corrupted download.\n"
                "Please try again."
            )

        all_structures.extend(structures)

    return all_structures


def download_structures(
    remote_url: str, local_path: Path, expected_file_hash: str, message: str = None
):
    def check_file_contents():
        file_hash = generate_checksum(local_path)
        return expected_file_hash == file_hash

    if local_path.exists():
        if check_file_contents():
            return
        else:
            raise ValueError(
                f"The dataset on disk at {local_path} has been corrupted.\n"
                "If you have made changes to this, "
                "please revert them or move/delete the file. Otherwise, "
                "please try again."
            )

    if message is not None:
        print(message)

    local_path.parent.mkdir(parents=True, exist_ok=True)
    download_thing(remote_url, local_path)

    if not local_path.exists():
        raise ValueError(
            "There was a problem downloading the dataset.\nPlease try again."
        )

    if not check_file_contents():
        # delete the file so we can try again later
        local_path.unlink()
        raise ValueError(
            "There was a problem downloading the dataset.\n"
            "What was downloaded does not match what we were expecting.\n"
            "Please try again."
        )

    assert local_path.exists()


def download_thing(url: str, save_to: Path) -> None:
    """Download a thing from the internet."""

    response = requests.get(url, stream=True)
    if response.status_code != 200:
        raise ValueError(f"Could not find {url}. Response code: {response.status_code}")

    total_size_in_bytes = int(response.headers.get("content-length", 0))
    block_size = 1024**2  # 1 MB

    N = math.ceil(total_size_in_bytes / block_size)
    blocks = response.iter_content(block_size)

    with open(save_to, "wb") as file:
        for data in progress_bar(blocks, N):
            file.write(data)
