from __future__ import annotations

from typing import Any, Callable, Sequence

import ase
import numpy as np

from load_atoms.dataset import AtomsDataset

__all__ = ["filter_by", "cross_validate_split"]


def filter_by(
    dataset: AtomsDataset | Sequence[ase.Atoms],
    *functions: Callable[[ase.Atoms], bool],
    **info_kwargs: Any,
) -> AtomsDataset:
    """
    Filter a dataset.

    Parameters
    ----------
    dataset
        The dataset to filter.
    functions
        Functions to filter the dataset by. Each function should take an
        ASE Atoms object as input and return a boolean.
    info_kwargs
        Keyword arguments to filter the dataset by. Only atoms objects with
        matching info keys and values will be returned.

    Returns
    -------
    AtomsDataset
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
    >>> water = filter_by(name="water")
    >>> len(water)
    1
    """

    def matches_info(structure: ase.Atoms) -> bool:
        for key, value in info_kwargs.items():
            if structure.info.get(key, None) != value:
                return False
        return True

    functions = (*functions, matches_info)

    def the_filter(structure: ase.Atoms) -> bool:
        return all(function(structure) for function in functions)

    return AtomsDataset.from_structures(
        [structure for structure in dataset if the_filter(structure)]
    )


def cross_validate_split(
    dataset: AtomsDataset | Sequence[ase.Atoms],
    fold,
    k: int = 5,
    n_test: int | None = None,
    seed: int = 0,
) -> tuple[AtomsDataset, AtomsDataset]:
    """
    Generate a shuffled train/test split for cross-validation.

    Parameters
    ----------
    dataset
        The dataset to split.
    fold : int
        The fold to use for testing.
    k
        The number of folds to use, by default 5.
    n_test
        The number of structures to use for testing, by
        this will be set to len(dataset) // k.
    seed
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
        AtomsDataset.from_structures([dataset[t] for t in train]),
        AtomsDataset.from_structures([dataset[t] for t in test]),
    )
