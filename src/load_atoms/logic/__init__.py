import warnings
from pathlib import Path
from typing import Any, Iterable, List, Optional, Union, overload

import numpy as np
from ase import Atoms
from ase.io import read
from yaml import dump

from load_atoms import backend
from load_atoms.shared import frontend_url, intersection, is_numpy, union
from load_atoms.shared.dataset_info import DatasetInfo


class Dataset:
    """
    A lightweight wrapper around a list of `ase.Atoms` objects.

    Examples
    -----------------

    >>> from load_atoms import dataset
    >>> ds = dataset("QM7")
    Please cite this dataset if you use it in your work.
    For more information, visit:
    https://jla-gardner.github.io/load-atoms/datasets/QM7.html

    `ds` is now a `Dataset` object - treat it like a list of `Atoms` objects:

    >>> from load_atoms.logic import Dataset
    >>> isinstance(ds, Dataset)
    True
    >>> len(ds)
    7165
    >>> ds[0]
    Atoms(symbols='CH4', pbc=False)

    Slicing the dataset returns a new `Dataset` object:

    >>> isinstance(ds[1:3], Dataset)
    True

    You can get a summary of the dataset by printing it:

    >>> print(ds)
    QM7:
    structures: 7,165
    atoms: 110,650
    species:
        H: 56.00%
        C: 32.32%
        N: 6.01%
        O: 5.40%
        S: 0.27%
    properties:
        per atom: ()
        per structure: (energy)
    """

    def __init__(
        self,
        structures: List[Atoms],
    ):
        if len(structures) == 1:
            warnings.warn(
                "Creating a dataset with a single structure. "
                "Typically, datasets contain multiple structures - "
                "did you mean to do this?",
                stacklevel=2,
            )

        self.structures = structures

    def __len__(self):
        return len(self.structures)

    @overload
    def __getitem__(self, index: int) -> Atoms:
        ...

    @overload
    def __getitem__(self, index: slice) -> "Dataset":
        ...

    @overload
    def __getitem__(self, index: np.ndarray) -> "Dataset":
        ...

    @overload
    def __getitem__(self, index: Iterable[int]) -> "Dataset":
        ...

    def __getitem__(self, index: Any):
        # if the passed index is a slice, return a new Dataset object:
        if isinstance(index, slice):
            return Dataset(self.structures[index])

        # if the index is iterable, return a new Dataset object:
        if hasattr(index, "__iter__"):
            # if the index is a np index, we want to keep the same behaviour
            # (e.g. passing array of indices, or a boolean array)
            if is_numpy(index):
                to_keep = np.arange(len(self))[index]
                return Dataset([self.structures[i] for i in to_keep])

            # some other iterable, e.g. a list of indices
            return Dataset([self.structures[i] for i in index])  # type: ignore

        # otherwise, we assume the index is an integer,
        # and return a single structure
        return self.structures[int(index)]

    def __iter__(self):
        return iter(self.structures)

    def __repr__(self):
        return summarise_dataset(self.structures)

    @classmethod
    def from_structures(cls, structures: List[Atoms]) -> "Dataset":
        """
        Create a dataset from a list of structures.

        Parameters
        ----------
        structures : List[Atoms]
            a list of structures
        """
        return cls(structures)

    @classmethod
    def from_file(cls, path: Path) -> "Dataset":
        """
        Load a dataset from an `ase.io.read`'able file.

        Parameters
        ----------
        path : Path
            the path to the file to load
        """
        return cls(read(path, index=":"))  # type: ignore


class DescribedDataset(Dataset):
    def __init__(
        self,
        structures: List[Atoms],
        description: DatasetInfo,
    ):
        super().__init__(structures)
        self.description = description

    @classmethod
    def from_id(
        cls,
        dataset_id: str,
        root: Union[Path, str, None] = None,
        verbose: bool = True,
    ) -> "Dataset":
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

        if verbose:
            print(usage_info(info))
        return cls(all_structures, info)

    def __repr__(self):
        return summarise_dataset(self.structures, self.description)


def usage_info(dataset: DatasetInfo) -> str:
    info = []
    if dataset.license is not None:
        info.append(
            f"This dataset is covered by the {dataset.license} license."
        )
    if dataset.citation is not None:
        info.append("Please cite this dataset if you use it in your work.")

    _url = frontend_url(dataset)
    info.append(f"For more information, visit:\n{_url}")

    return "\n".join(info)


def summarise_dataset(
    structures: Union[List[Atoms], Dataset],
    description: Optional[DatasetInfo] = None,
) -> str:
    name = description.name if description is not None else "Dataset"
    N = len(structures)
    number_atoms = sum([len(structure) for structure in structures])

    per_atom_properties = intersection(
        structure.arrays.keys() for structure in structures
    )
    per_atom_properties -= {"numbers", "positions"}
    per_structure_properties = intersection(
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
