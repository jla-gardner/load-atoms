"""
The backend is responsible for downloading the datasets when they are first loaded, and for loading the datasets into memory.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Dict

import yaml
from ase.io import read

from load_atoms.classes import Info

DATASETS_DIR = Path(__file__).parent / "datasets"


def _load_dataset(name):
    """Load a dataset from the datasets directory."""

    files = DATASETS_DIR.glob(f"{name}.*")
    files = [f for f in files if not f.suffix == ".yaml"]

    if files:
        assert len(files) == 1
        return read(files[0], index=":")

    _download_dataset(name)
    return _load_dataset(name)


def _download_dataset(name):
    """Download a dataset from the internet."""

    raise NotImplementedError


def _get_info(dataset_name: str) -> Dict[str, str]:
    """Get information about a dataset."""

    path = DATASETS_DIR / f"{dataset_name}.yaml"

    if not path.exists():
        raise FileNotFoundError(f"Dataset {dataset_name} not found.")

    return Info(name=dataset_name, **yaml.safe_load(path.read_text()))
