from __future__ import annotations

from pathlib import Path

import ase
from ase.io import read

from .atoms_dataset import AtomsDataset, InMemoryAtomsDataset
from .database import backend
from .visualisation import view

__version__ = "0.3.2"
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
    >>> dataset = load_dataset("QM9")
    ╭───────────────────────────────── QM9 ─────────────────────────────────╮
    │                                                                       │
    │   Downloading dsgdb9nsd.xyz.tar.bz2 ━━━━━━━━━━━━━━━━━━━━ 100% 00:09   │
    │   Extracting dsgdb9nsd.xyz.tar.bz2  ━━━━━━━━━━━━━━━━━━━━ 100% 00:18   │
    │   Processing files                  ━━━━━━━━━━━━━━━━━━━━ 100% 00:19   │
    │   Caching to disk                   ━━━━━━━━━━━━━━━━━━━━ 100% 00:02   │
    │                                                                       │
    │            The QM9 dataset is covered by the CC0 license.             │
    │        Please cite the QM9 dataset if you use it in your work.        │
    │          For more information about the QM9 dataset, visit:           │
    │                            load-atoms/QM9                             │
    ╰───────────────────────────────────────────────────────────────────────╯
    >>> dataset
    QM9:
        structures: 133,885
        atoms: 2,407,753
        species:
            H: 51.09%
            C: 35.16%
            O: 7.81%
            N: 5.80%
            F: 0.14%
        properties:
            per atom: (partial_charges)
            per structure: (
                A, B, C, Cv, G, H, U, U0, alpha,
                frequencies, gap, geometry, homo, inchi, index,
                lumo, mu, r2, smiles, zpve
            )


    Optionally save a dataset to an explicit root directory:

    >>> load_dataset("QM9", root="./my-datasets")

    Wrap a list of structures in a dataset:

    >>> load_dataset([Atoms("H2O"), Atoms("H2O2")])

    Load a dataset from a file:

    >>> load_dataset("path/to/file.xyz")
    """

    if isinstance(thing, list) and all(isinstance(s, ase.Atoms) for s in thing):
        # thing is a list of structures
        return InMemoryAtomsDataset(thing)

    if not isinstance(thing, (Path, str)):
        raise TypeError(
            f"Could not load dataset from {thing}. "
            "Please provide a string, a list of structures, "
            "or a path to a file."
        )

    if Path(thing).exists() and Path(thing).is_file():
        # thing is a string/path to a file that exists
        # assume it is a file containing structures and load them
        structures = read(Path(thing), index=":")
        if isinstance(structures, ase.Atoms):
            structures = [structures]
        return InMemoryAtomsDataset(structures)

    if isinstance(thing, Path):
        # thing is a path to a file that does not exist
        raise ValueError(f"The provided path does not exist. ({thing})")

    # assume thing is a dataset ID, and try to load it
    if root is None:
        root = Path.home() / ".load-atoms"
    return backend.load_dataset_by_id(thing, Path(root))
