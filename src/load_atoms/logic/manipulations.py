"""
convenience functions for manipulating datasets
"""

from typing import Callable, Optional, Sequence, Tuple, Union

import numpy as np
from ase import Atoms

from load_atoms.logic import Dataset

__all__ = ["filter_by", "cross_validate_split"]

FilterFunction = Callable[[Atoms], bool]


def filter_by(
    dataset: Union[Dataset, Sequence[Atoms]],
    *functions: FilterFunction,
    **info_kwargs,
) -> Dataset:
    """
    Filter a dataset.

    Parameters
    ----------
    dataset : Union[Dataset, Sequence[Atoms]]
        The dataset to filter.
    functions : FilterFunction
        Functions to filter the dataset by. Each function should take an
        ASE Atoms object as input and return a boolean.
    info_kwargs : dict
        Keyword arguments to filter the dataset by. Only atoms objects with
        matching info keys and values will be returned.

    Returns
    -------
    Dataset
        The filtered dataset.

    Examples
    --------
    >>> from ase import Atoms
    >>> from load_atoms.manipulations import filter_by
    >>> structures = [
    ...     Atoms("H2O", info=dict(name="water")),
    ...     Atoms("H2O2", info=dict(name="hydrogen peroxide")),
    ...     Atoms("CH4", info=dict(name="methane")),
    ... ]
    >>> small = filter_by(
    ...     structures,
    ...     lambda structure: len(structure) < 4,
    ... )
    >>> len(small)
    1
    """

    def matches_info(structure: Atoms) -> bool:
        for key, value in info_kwargs.items():
            if structure.info.get(key, None) != value:
                return False
        return True

    functions = (*functions, matches_info)

    def the_filter(structure: Atoms) -> bool:
        return all(function(structure) for function in functions)

    return Dataset.from_structures(
        [structure for structure in dataset if the_filter(structure)]
    )


def cross_validate_split(
    dataset: Union[Dataset, Sequence[Atoms]],
    fold,
    k=5,
    n_test: Optional[int] = None,
    seed: int = 0,
) -> Tuple[Dataset, Dataset]:
    """
    Generate a shuffled train/test split for cross-validation.

    Parameters
    ----------
    dataset : Union[Dataset, Sequence[Atoms]]
        The dataset to split.
    fold : int
        The fold to use for testing.
    k : int, optional
        The number of folds to use, by default 5.
    n_test : Optional[int], optional
        The number of structures to use for testing, by default None.
        If None, this will be set to len(dataset) // k.
    seed : int, optional
        The random seed to use, by default 0.

    Returns
    -------
    Tuple[Dataset, Dataset]
        The train and test datasets.

    Examples
    --------
    >>> from ase import Atoms
    >>> from load_atoms.manipulations import cross_validate_split
    >>> structures = [
    ...     Atoms("H2O", info=dict(name="water")),
    ...     Atoms("H2O2", info=dict(name="hydrogen peroxide")),
    ...     Atoms("CH4", info=dict(name="methane")),
    ... ]
    >>> train, test = cross_validate_split(structures, fold=0, k=3)
    >>> len(train)
    2
    >>> len(test)
    1
    """

    if n_test is None:
        n_test = len(dataset) // k

    idxs = np.arange(len(dataset))
    np.random.RandomState(seed).shuffle(idxs)
    idxs = np.roll(idxs, fold * len(idxs) // k)
    train, test = idxs[:-n_test], idxs[-n_test:]

    return (
        Dataset.from_structures([dataset[t] for t in train]),
        Dataset.from_structures([dataset[t] for t in test]),
    )
