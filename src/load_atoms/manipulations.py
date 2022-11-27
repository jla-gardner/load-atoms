from typing import Callable, Sequence

from ase import Atoms

from load_atoms.classes import Dataset

FilterFunction = Callable[[Atoms], bool]


def filter_by(
    dataset: Dataset, *functions: Sequence[FilterFunction], **kwargs
) -> Dataset:
    """Filter a dataset by a given property."""

    by_kwargs = [
        structure
        for structure in dataset
        if all(structure.info.get(key, None) == value for key, value in kwargs.items())
    ]

    return [
        structure
        for structure in by_kwargs
        if all(func(structure) for func in functions)
    ]
