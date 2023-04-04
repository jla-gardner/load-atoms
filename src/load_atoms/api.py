from pathlib import Path
from typing import List, Union

from ase import Atoms

from load_atoms.dataset import Dataset


def dataset(
    thing: Union[str, List[Atoms], Path],
    root: Union[str, Path] = None,
) -> Dataset:
    """
    Load a dataset by name or from a list of structures.

    Parameters
    ----------
    thing
        A dataset id, a list of structures, or a path to a file.
    root
        The root directory to use when loading a dataset by id.
        If not provided, the default root directory will be used.

    Returns
    -------
    Dataset
        The loaded dataset.

    Examples
    --------
    >>> from load_atoms import dataset
    >>> from ase import Atoms
    >>> from ase.io import read, write
    >>> dataset("qm7")
    >>> dataset("qm7", root="./my-datasets")
    >>> dataset([Atoms("H2O"), Atoms("H2O2")])
    >>> dataset("path/to/file.xyz")
    """

    if isinstance(thing, list) and all(isinstance(s, Atoms) for s in thing):
        # thing is a list of structures
        return Dataset.from_structures(thing)

    if not isinstance(thing, (Path, str)):
        raise TypeError(
            f"Could not load dataset from {thing}. "
            "Please provide a string, a list of structures, or a path to a file."
        )

    if Path(thing).exists():
        # thing is a string/path to a file that exists
        # assume it is a file containing structures and load them
        return Dataset.from_file(Path(thing))

    if isinstance(thing, Path):
        # thing is a path to a file that does not exist
        raise ValueError(f"The provided path does not exist. ({thing})")

    # assume thing is a dataset ID, and try to load it
    return Dataset.from_id(thing, root)
