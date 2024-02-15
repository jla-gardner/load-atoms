from __future__ import annotations

import warnings
from pathlib import Path
from typing import Any, Callable, Iterable, Iterator, overload

import ase
import numpy as np
from ase import Atoms
from ase.io import read
from yaml import dump

from . import backend
from .dataset_info import DatasetInfo
from .utils import LazyMapping, frontend_url, intersect, union


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

    if isinstance(thing, list) and all(isinstance(s, Atoms) for s in thing):
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


class AtomsDataset:
    """
    A lightweight wrapper around a list of :class:`ase.Atoms` objects.

    See :func:`~load_atoms.load_dataset` for the recommended entry point
    for this class.

    Parameters
    ----------
    structures
        The structures comprising the dataset.
    """

    def __init__(self, structures: list[ase.Atoms]):
        if len(structures) == 1:
            warnings.warn(
                "Creating a dataset with a single structure. "
                "Typically, datasets contain multiple structures - "
                "did you mean to do this?",
                stacklevel=2,
            )

        self.structures = structures

        keys, loader = _get_info_loader(structures)
        self.info: LazyMapping[str, Any] = LazyMapping(keys, loader)
        """A key-value mapping of per-structure properties."""

        keys, loader = _get_arrays_loader(structures)
        self.arrays: LazyMapping[str, np.ndarray] = LazyMapping(keys, loader)
        """A key-value mapping of per-atom properties."""

    @property
    def structure_sizes(self) -> np.ndarray:
        """The number of atoms in each structure."""
        return np.array([len(s) for s in self.structures])

    @property
    def n_atoms(self) -> int:
        """The total number of atoms in the dataset."""
        return self.structure_sizes.sum()

    def __len__(self) -> int:
        """The number of structures in the dataset."""
        return len(self.structures)

    @overload
    def __getitem__(self, index: int) -> ase.Atoms:
        ...

    @overload
    def __getitem__(self, index: slice) -> AtomsDataset:
        ...

    @overload
    def __getitem__(self, index: np.ndarray) -> AtomsDataset:
        ...

    @overload
    def __getitem__(self, index: Iterable[int]) -> AtomsDataset:
        ...

    def __getitem__(self, index: Any):
        """
        Index the dataset.

        Parameters
        ----------
        index
            specifies the structure/s to select from the dataset.

        Examples
        --------

        >>> from load_atoms import load_dataset
        >>> qm7 = load_dataset("QM7")

        Get the first structure in the dataset:

        >>> qm7[0]  # returns the first structure in the dataset
        Atoms(symbols='CH4', pbc=False)

        Create a new dataset with the first 10 structures:

        >>> qm7[:10]
        Dataset:
            structures: 10
            atoms: 77
            species:
                H: 67.53%
                C: 28.57%
                O: 3.90%
            properties:
                per atom: ()
                per structure: (energy)

        Create a new dataset of high energy structures using a mask
        (see :func:`~load_atoms.manipulations.filter_by` for a more convenient
        way to do this):

        >>> mask = qm7.info["energy"] / qm7.structure_sizes > -4
        >>> qm7[mask]
        Dataset:
            structures: 155
            atoms: 2,636
            species:
                H: 63.28%
                C: 22.76%
                N: 8.27%
                O: 4.78%
                S: 0.91%
            properties:
                per atom: ()
                per structure: (energy)
        """
        # if the passed index is a slice, return a new Dataset object:
        if isinstance(index, slice):
            return AtomsDataset(self.structures[index])

        # if the index is iterable, return a new Dataset object:
        if hasattr(index, "__iter__"):
            # if the index is a np index, we want to keep the same behaviour
            # (e.g. passing array of indices, or a boolean array)
            if isinstance(index, np.ndarray):
                to_keep = np.arange(len(self))[index]
                return AtomsDataset([self.structures[i] for i in to_keep])

            # some other iterable, e.g. a list of indices
            return AtomsDataset([self.structures[i] for i in index])  # type: ignore

        # otherwise, we assume the index is an integer,
        # and return a single structure
        return self.structures[int(index)]

    def __iter__(self) -> Iterator[ase.Atoms]:
        """
        Iterate over the structures in the dataset.
        """

        return iter(self.structures)

    def __repr__(self):
        return summarise_dataset(self.structures)


def usage_info(info: DatasetInfo) -> str:
    lines = []
    if info.license is not None:
        lines.append(
            f"The {info.name} dataset is covered by the "
            f"{info.license} license."
        )
    if info.citation is not None:
        lines.append(
            f"Please cite the {info.name} dataset "
            "if you use it in your work."
        )
    lines.append(
        f"For more information about the {info.name} dataset, visit\n"
        f"{frontend_url(info)}."
    )

    return "\n".join(lines)


class DescribedDataset(AtomsDataset):
    def __init__(
        self,
        structures: list[Atoms],
        description: DatasetInfo,
    ):
        super().__init__(structures)
        self.description = description

    @classmethod
    def from_id(
        cls,
        dataset_id: str,
        root: Path | (str | None) = None,
        verbose: bool = True,
    ) -> AtomsDataset:
        """
        Load a dataset by id.

        Parameters
        ----------
        dataset_id : str
            the id of the dataset to load
        root : Union[Path, str, None], optional
            the root directory to cache the dataset to, by default None
        verbose : bool, optional
            whether to print information about the dataset, by default True
        """

        if root is None:
            root = Path.home() / ".load-atoms"
        root = Path(root)

        all_structures, info = backend.get_structures_for(dataset_id, root)

        # remove annoying automatic ASE calculators
        for structure in all_structures:
            del structure.calc

        if verbose:
            print(usage_info(info))
        return cls(all_structures, info)

    def __repr__(self):
        return summarise_dataset(self.structures, self.description)


def _get_info_loader(
    structures: list[Atoms],
) -> tuple[list[str], Callable[[str], Any]]:
    keys = intersect(structure.info.keys() for structure in structures)

    def loader(key: str):
        return np.array([structure.info[key] for structure in structures])

    return list(keys), loader


def _get_arrays_loader(
    structures: list[Atoms],
) -> tuple[list[str], Callable[[str], Any]]:
    keys = intersect(structure.arrays.keys() for structure in structures)

    def loader(key: str):
        return np.concatenate(
            [structure.arrays[key] for structure in structures]
        )

    return list(keys), loader


def summarise_dataset(
    structures: list[Atoms] | AtomsDataset,
    description: DatasetInfo | None = None,
) -> str:
    name = description.name if description is not None else "Dataset"
    N = len(structures)
    number_atoms = sum([len(structure) for structure in structures])

    per_atom_properties = intersect(
        structure.arrays.keys() for structure in structures
    )
    per_atom_properties -= {"numbers", "positions"}
    per_structure_properties = intersect(
        structure.info.keys() for structure in structures
    )

    species = union(
        structure.get_chemical_symbols() for structure in structures
    )
    species_counts = {
        s: sum(
            [
                structure.get_chemical_symbols().count(s)
                for structure in structures
            ]
        )
        for s in species
    }
    species_counts = {
        k: f"{v / number_atoms:.2%}"
        for k, v in sorted(
            species_counts.items(), key=lambda item: item[1], reverse=True
        )
    }

    if N >= 1000:
        N = f"{N:,}"
    if number_atoms >= 1000:
        number_atoms = f"{number_atoms:,}"

    fields = {
        "structures": N,
        "atoms": number_atoms,
        "species": species_counts,
        "properties": {
            "per atom": "(" + ", ".join(per_atom_properties) + ")",
            "per structure": "(" + ", ".join(per_structure_properties) + ")",
        },
    }

    return dump({name: fields}, sort_keys=False, indent=4)
