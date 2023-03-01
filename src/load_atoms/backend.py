"""
The backend is responsible for downloading the datasets when they 
are first loaded, and for loading these datasets into memory, via
the `load_dataset_for` function. 
"""

from pathlib import Path
from typing import Tuple, Union

import requests
from ase.io import read

from load_atoms.checksums import generate_checksum
from load_atoms.database import DatasetDescription, get_description_of, print_info_for
from load_atoms.dataset import Dataset
from load_atoms.util import BASE_REMOTE_URL, DEFAULT_DOWNLOAD_DIR, progress_bar


def load_dataset_for(
    dataset_id: str, root: Union[str, Path] = None
) -> Tuple[str, Dataset]:
    """Get a dataset from a dataset ID."""

    if root is None:
        root = DEFAULT_DOWNLOAD_DIR
    else:
        root = Path(root)

    dataset_description = get_description_of(dataset_id)

    download_if_needed(dataset_description, root)
    print_info_for(dataset_description)

    all_structures = []
    for filename in dataset_description.files:
        all_structures.extend(read(root / filename, index=":"))

    return Dataset(all_structures, dataset_description.name)


def download_if_needed(dataset: DatasetDescription, root: Path) -> None:
    """Download a dataset if it is not already present."""

    for filename, file_hash in dataset.files.items():
        local_path = root / filename
        if not local_path.exists():
            print(
                f"Downloading {filename} from https://github.com/jla-gardner/load-atoms/"
            )
            local_path.parent.mkdir(parents=True, exist_ok=True)
            remote_url = BASE_REMOTE_URL + filename
            _download_thing(remote_url, local_path)

        assert local_path.exists(), f"Could not download {filename} from {remote_url}"
        assert file_hash == generate_checksum(
            local_path
        ), f"Checksum of {filename} does not match expected value."


def _download_thing(url: str, save_to: Path) -> None:
    """Download a thing from the internet."""

    response = requests.get(url, stream=True)
    assert response.status_code == 200, f"Could not find {url}"
    total_size_in_bytes = int(response.headers.get("content-length", 0))
    block_size = 1024**2  # 1 MB

    N = total_size_in_bytes // block_size
    blocks = response.iter_content(block_size)

    with open(save_to, "wb") as file:
        for data in progress_bar(blocks, N):
            file.write(data)
