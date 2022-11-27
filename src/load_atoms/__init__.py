from pathlib import Path
from typing import Union

import numpy as np
from IPython.display import Markdown, display

from load_atoms.backend import _get_info, _load_dataset
from load_atoms.classes import Dataset
from load_atoms.manipulations import filter_by
from load_atoms.util import pad


def load_dataset(name: str, root: Union[str, Path] = ".") -> Dataset:
    """Load a dataset by name."""

    dataset = _load_dataset(name, root)
    info = _get_info(name)

    n_structures = len(dataset)
    n_atoms = sum(len(structure) for structure in dataset)

    print(
        f"""\
Loaded {info.name}, containing {n_structures:,} structures and {n_atoms:,} atoms.
The use of this dataset is licensed under {info.license}.\
    """
    )

    return dataset


def info(name: str) -> None:
    """Print information about a dataset."""

    info = _get_info(name)

    fields = ["description", "citation", "license"]

    _info = f"# {info.name} \n\n"
    for field in fields:
        value = getattr(info, field)
        if value is not None:
            _info += f"""\
## {field.title()}

{value}
"""
    display(Markdown(_info))


def cross_validate_split(
    dataset: Dataset, fold, folds=5, n_test: int = None, seed: int = 0
) -> Dataset:
    """Generate a shuffled train/test split for cross-validation."""

    if n_test is None:
        n_test = len(dataset) // folds

    idxs = np.arange(len(dataset))
    np.random.RandomState(seed).shuffle(idxs)
    idxs = np.roll(idxs, fold * len(idxs) // folds)
    train, test = idxs[:-n_test], idxs[-n_test:]

    return (
        [dataset[t] for t in train],
        [dataset[t] for t in test],
    )
