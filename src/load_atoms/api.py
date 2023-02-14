from pathlib import Path
from typing import List, Union

from ase import Atoms
from ase.io import read

from load_atoms.backend import load_dataset_for
from load_atoms.database import is_known_dataset
from load_atoms.dataset import Dataset


def dataset(
    thing: Union[str, List[Atoms], Path],
    root: Union[str, Path] = None,
    name: str = None,
) -> Dataset:
    """Load a dataset by name or from a list of structures."""

    if isinstance(thing, str) and Path(thing).exists():
        # thing is a string/path to a dataset
        thing = Path(thing)

    if isinstance(thing, Path):
        # reading structures from a local file, and wrapping them in a Dataset
        assert thing.exists(), f"File {thing} does not exist."
        if name is None:
            name = thing.stem
        structures = read(thing, index=":")
        return Dataset(structures, name)

    elif isinstance(thing, str):
        # assume thing is a dataset ID, and try to load it
        assert is_known_dataset(thing), f"Dataset {thing} is not known."
        return load_dataset_for(thing, root)

    elif isinstance(thing, list) and all(isinstance(s, Atoms) for s in thing):
        # thing is a list of structures
        return Dataset(thing, name)

    raise ValueError(
        f"Could not load dataset from {thing}. "
        "Please provide a string, a list of structures, or a path to a file."
    )
