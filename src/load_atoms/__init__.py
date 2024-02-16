from __future__ import annotations

from pathlib import Path

import ase
from ase.io import read

from .atoms_dataset import AtomsDataset, DescribedDataset
from .visualise import view

__version__ = "0.1.6"
__all__ = ["load_dataset", "view"]


def load_dataset(
    thing: str | list[ase.Atoms] | Path,
    root: str | Path | None = None,
) -> AtomsDataset:
    """
    Load a dataset by name or from a list of structures.

    Parameters
    ----------
    thing
        A dataset id, a list of structures, or a path to a file.
    root
        The root directory to use when loading a dataset by id. If not
        provided, the default root directory (:code:`~/.load-atoms`)
        will be used.

    Examples
    --------
    Load a dataset by id:

    >>> from load_atoms import load_dataset
    >>> dataset = load_dataset("C-GAP-17")

    Optionally save a dataset to an explicit root directory:

    >>> dataset("C-GAP-17", root="./my-datasets")

    Wrap a list of structures in a dataset:

    >>> dataset([Atoms("H2O"), Atoms("H2O2")])

    Load a dataset from a file:

    >>> dataset("path/to/file.xyz")
    """

    if isinstance(thing, list) and all(isinstance(s, ase.Atoms) for s in thing):
        # thing is a list of structures
        return AtomsDataset(thing)

    if not isinstance(thing, (Path, str)):
        raise TypeError(
            f"Could not load dataset from {thing}. "
            "Please provide a string, a list of structures, "
            "or a path to a file."
        )

    if Path(thing).exists():
        # thing is a string/path to a file that exists
        # assume it is a file containing structures and load them
        structures = read(Path(thing), index=":")
        return AtomsDataset(structures)  # type: ignore

    if isinstance(thing, Path):
        # thing is a path to a file that does not exist
        raise ValueError(f"The provided path does not exist. ({thing})")

    # assume thing is a dataset ID, and try to load it
    return DescribedDataset.from_id(thing, root)
