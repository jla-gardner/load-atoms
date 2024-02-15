from __future__ import annotations

from pathlib import Path

import ase
from ase.io import read

from .atoms_dataset import AtomsDataset, DescribedDataset
from .visualise import view

__version__ = "0.1.5"
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
    The following are all viable ways to load a dataset:

    * by id: :code:`dataset("QM7")`
    * by id, with a custom root directory:
      :code:`dataset("QM7", root="./my-datasets")`
    * from a list of structures: :code:`dataset([Atoms("H2O"), Atoms("H2O2")])`
    * from a file: :code:`dataset("path/to/file.xyz")`
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
