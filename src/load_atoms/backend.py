"""
The backend is responsible for downloading the datasets when they 
are first loaded, and for loading these datasets into memory, via
the `_load_dataset` function. 
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Union

import requests
import yaml
from ase.io import read
from tqdm import tqdm

from load_atoms.classes import Dataset, Info

DATASETS_DIR = Path(__file__).parent / "datasets"


def _load_dataset(name: str, root: Union[str, Path]) -> Dataset:
    """
    Load a dataset from the datasets directory.

    If the dataset is not present, download it first.
    """

    path = Path(root) / (name + ".extxyz")

    if not path.exists():
        print(f"Dataset {name} not found. Downloading...")
        url = _get_url(name)
        _download_thing(url, path)

    return read(path, index=":")


def _download_thing(url: str, save_to: Path) -> None:
    """Download a thing from the internet."""

    response = requests.get(url, stream=True)
    total_size_in_bytes = int(response.headers.get("content-length", 0))
    block_size = 1024**2  # 1 MB

    def bar():
        return tqdm(
            total=total_size_in_bytes,
            unit="iB",
            unit_scale=True,
            position=0,
            leave=True,
        )

    with open(save_to, "wb") as file, bar() as progress_bar:
        for data in response.iter_content(block_size):
            progress_bar.update(len(data))
            file.write(data)


def _get_url(dataset_name: str):
    """Get the URL (from the github repo) of a dataset."""

    BASE = "https://github.com/jla-gardner/load-atoms/raw/main/src/load_atoms/datasets"
    return f"{BASE}/{dataset_name}.extxyz"


def _get_info(dataset_name: str) -> Dict[str, str]:
    """Get information about a dataset."""

    path = DATASETS_DIR / f"{dataset_name}.yaml"

    if not path.exists():
        raise FileNotFoundError(f"Dataset {dataset_name} not found.")

    _dict = {
        key: value.strip() for key, value in yaml.safe_load(path.read_text()).items()
    }

    return Info(name=dataset_name, **_dict)
