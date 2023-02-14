"""
The backend is responsible for downloading the datasets when they 
are first loaded, and for loading these datasets into memory, via
the `_load_dataset` function. 
"""

from pathlib import Path
from typing import Tuple, Union

import requests
from ase.io import read

from load_atoms.database import DatabaseEntry, get_database_entry_for, print_info_for
from load_atoms.dataset import Dataset
from load_atoms.util import BASE_REMOTE_URL, progress_bar


def load_dataset_for(
    dataset_id: str, root: Union[str, Path] = None
) -> Tuple[str, Dataset]:
    """Get a dataset from a dataset ID."""

    if root is None:
        root = Path(__file__).parent / "datasets"
    else:
        root = Path(root) / "datasets"

    db_entry = get_database_entry_for(dataset_id)

    download_if_needed(db_entry, root)
    print_info_for(db_entry)

    all_structures = []
    for filename in db_entry.filenames:
        all_structures.extend(read(root / filename, index=":"))
    return Dataset(all_structures, db_entry.name)


def download_if_needed(db_entry: DatabaseEntry, root: Path) -> None:
    """Download a dataset if it is not already present."""

    for filename in db_entry.filenames:
        local_path = root / filename
        if local_path.exists():
            continue

        print(f"Downloading {filename} from https://github.com/jla-gardner/load-atoms/")
        local_path.parent.mkdir(parents=True, exist_ok=True)
        remote_url = BASE_REMOTE_URL + filename
        _download_thing(remote_url, local_path)


def _download_thing(url: str, save_to: Path) -> None:
    """Download a thing from the internet."""

    response = requests.get(url, stream=True)
    assert response.status_code == 200, f"Could not download {url}"
    total_size_in_bytes = int(response.headers.get("content-length", 0))
    block_size = 1024**2  # 1 MB

    N = total_size_in_bytes // block_size
    blocks = response.iter_content(block_size)

    with open(save_to, "wb") as file:
        for data in progress_bar(blocks, N):
            file.write(data)
