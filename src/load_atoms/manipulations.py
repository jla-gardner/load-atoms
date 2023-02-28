from typing import Callable, Sequence, Union

import numpy as np
from ase import Atoms

from load_atoms.dataset import Dataset

FilterFunction = Callable[[Atoms], bool]


def filter_by(
    dataset: Union[Dataset, Sequence[Atoms]],
    *functions: Sequence[FilterFunction],
    **kwargs
) -> Dataset:
    """Filter a dataset by a given property."""

    structures_filtered_by_kwargs = [
        structure
        for structure in dataset
        if all(structure.info.get(key, None) == value for key, value in kwargs.items())
    ]

    return Dataset(
        [
            structure
            for structure in structures_filtered_by_kwargs
            if all(func(structure) for func in functions)
        ]
    )


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
