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
        for function in functions:
            if not function(structure):
                return False
        return True

    return Dataset.from_structures(
        [structure for structure in dataset if the_filter(structure)]
    )


def cross_validate_split(
    dataset: Union[Dataset, Sequence[Atoms]],
    fold,
    k=5,
    n_test: Optional[int] = None,
    by_config_type: Optional[str] = None,
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
    by_config_type : Optional[str], optional
        Whether to split the dataset evenly by config_type, by default None.
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

    if by_config_type is not None:
        # the user needs to supply the str so we know what to split by. for example some may use 'config_type' and others may use 'config_type_1' etc..
        # the aim of this is to ensure that we have a balanced dataset for each fold and that we have the same number of each config_type in each fold
        # this is important for the training of the model
        # we need to split the dataset by config_type

        # get the unique config_types
        config_types = np.unique(
            [structure.info[by_config_type] for structure in dataset]
        )

        # get the indices of the config_types
        config_type_idxs = [
            np.where(
                [structure.info[by_config_type] == config_type for structure in dataset]
            )[0]
            for config_type in config_types
        ]

        # we have n_test total, we should split this evenly between the config_types
        n_test_per_config_type = n_test // len(config_types)

        # Initialize an array to hold test indices
        remainder = n_test % len(config_types)

        np.random.RandomState(seed).shuffle(config_type_idxs)

        test_indices = np.array([])

        for i in range(len(config_types)):
            # Determine the number of testing structures for this config_type
            num_testing_for_config = n_test_per_config_type + (
                1 if i < remainder else 0
            )

            # Randomly choose indices for testing without replacement
            chosen_indices = np.random.RandomState(seed).choice(
                config_type_idxs[i], num_testing_for_config, replace=False
            )

            # Append the chosen indices to the test_indices array
            test_indices = np.concatenate((test_indices, chosen_indices))

        # get the indices for the train set
        train_indices = np.setdiff1d(np.arange(len(dataset)), test_indices)

        # shuffle the indices
        np.random.RandomState(seed).shuffle(train_indices)
        np.random.RandomState(seed).shuffle(test_indices)

    else:
        idxs = np.arange(len(dataset))
        np.random.RandomState(seed).shuffle(idxs)
        idxs = np.roll(idxs, fold * len(idxs) // k)
        train_indices, test_indices = idxs[:-n_test], idxs[-n_test:]

    return (
        Dataset.from_structures([dataset[t] for t in train_indices]),
        Dataset.from_structures([dataset[t] for t in test_indices]),
    )
