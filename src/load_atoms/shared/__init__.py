from pathlib import Path
from typing import Iterable

import numpy as np

# this file is at <root>/src/load_atoms/util.py
# the datasets are at <root>/src/load_atoms/datasets
DATASETS_DIR = (Path(__file__).parent / "datasets").resolve()
BASE_REMOTE_URL = (
    "https://github.com/jla-gardner/load-atoms/raw/main/src/load_atoms/datasets/"
)
FRONTEND_URL = "https://jla-gardner.github.io/load-atoms/datasets/"


class UnknownDatasetException(Exception):
    def __init__(self, dataset_id):
        super().__init__(f"Unknown dataset: {dataset_id}")


def is_numpy(thing):
    """Check if a thing is a numpy array."""
    return isinstance(thing, np.ndarray)


def union(things: Iterable[Iterable]):
    """Get the set union of a list of iterables."""
    return set.union(*map(set, things))


def intersection(things: Iterable[Iterable]):
    """Get the set intersection of a list of iterables."""
    return set.intersection(*map(set, things))


def lpad(s, indent=4):
    return "\n".join(" " * indent + line for line in s.splitlines())


def frontend_url(dataset_info):
    """Get the URL for a dataset."""
    return FRONTEND_URL + dataset_info.name + ".html"