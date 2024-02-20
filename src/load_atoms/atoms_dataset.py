from __future__ import annotations

import warnings
from collections import defaultdict
from pathlib import Path
from typing import Any, Callable, Iterable, Iterator, overload

import ase
import numpy as np
from ase import Atoms
from yaml import dump

from .database import DatabaseEntry, backend
from .utils import LazyMapping, frontend_url, intersect, random_split, union


class AtomsDataset:
    """An immutable wrapper around a list of :class:`ase.Atoms` objects."""

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
        """
        A key-value mapping of per-structure properties.
        
        Examples
        --------
        Scalar per-structure properties are turned into an 
        :class:`np.ndarray <numpy.ndarray>`:

        >>> dataset = load_dataset("C-GAP-17")
        >>> dataset.info["energy"]
        array([-9847.661671, -9886.440245, -9916.681692, ...,  -632.464825,
                -632.146922,  -632.944571])

        Non-scalar properties are concatenated along a new axis:

        >>> c_gap_20 = load_dataset("C-GAP-20")
        >>> c_gap_20.info["virial"].shape
        (6088, 3, 3)
        """

        keys, loader = _get_arrays_loader(structures)
        self.arrays: LazyMapping[str, np.ndarray] = LazyMapping(keys, loader)
        """
        A key-value mapping of per-atom properties.
        
        Example
        -------
        Per-atom properties are concatenated along the first axis:

        >>> dataset = load_dataset("C-GAP-17")
        >>> dataset.arrays["forces"].shape
        (284965, 3)
        """

    @property
    def structure_sizes(self) -> np.ndarray:
        """The number of atoms in each structure."""
        return np.array([len(s) for s in self.structures])

    @property
    def n_atoms(self) -> int:
        """The total number of atoms in the dataset."""
        return int(self.structure_sizes.sum())

    def filter_by(
        self, *functions: Callable[[ase.Atoms], bool], **info_kwargs: Any
    ) -> AtomsDataset:
        """
        Return a new dataset containing only the structures that match the
        given criteria.

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

        Example
        -------
        Get small, amorphous structures with large forces:

        .. code-block:: pycon
            :emphasize-lines: 3-7

            >>> from load_atoms import load_dataset
            >>> dataset = load_dataset("C-GAP-17")
            >>> dataset.filter_by(
            ...     lambda structure: len(structure) < 50,
            ...     lambda structure: structure.arrays["force"].max() > 5,
            ...     config_type="bulk_amo"
            ... )
            Dataset:
                structures: 609
                atoms: 23,169
                species:
                    C: 100.00%
                properties:
                    per atom: (force)
                    per structure: (config_type, detailed_ct, split, energy)
        """

        def matches_info(structure: ase.Atoms) -> bool:
            for key, value in info_kwargs.items():
                if structure.info.get(key, None) != value:
                    return False
            return True

        functions = (*functions, matches_info)

        def the_filter(structure: ase.Atoms) -> bool:
            return all(f(structure) for f in functions)

        return AtomsDataset(list(filter(the_filter, self)))

    def random_split(
        self,
        splits: list[float] | list[int],
        seed: int = 42,
        keep_ratio: str | None = None,
    ) -> list[AtomsDataset]:
        r"""
        Randomly split the dataset into multiple, disjoint parts.

        Parameters
        ----------
        splits
            The number of structures to put in each split.
            If a list of :class:`float`s, the splits will be
            calculated as a fraction of the dataset size.
        seed
            The random seed to use for shuffling the dataset.
        keep_ratio
            If not :code:`None`, splits will be generated to maintain the
            ratio of structures in each split with the specified :code:`.info`
            value.

        Returns
        -------
        list[AtomsDataset]
            A list of new datasets, each containing a subset of the original

        Examples
        --------
        Split a :code:`dataset` into 80% training and 20% test sets:

        >>> train, test = dataset.random_split([0.8, 0.2])

        Split a :code:`dataset` into 3 parts:

        >>> train, val, test = dataset.random_split([1_000, 100, 100])

        Maintain the ratio of structures with various :code:`config_type`\ s:

        >>> from load_atoms import load_dataset
        >>> import numpy as np
        >>> def ratios(thing):
        ...     values, counts = np.unique(thing, return_counts=True)
        ...     max_len = max(len(str(v)) for v in values)
        ...     for v, c in zip(values, counts / counts.sum()):
        ...         print(f"{v:>{max_len}}: {c:>5.1%}")
        ...
        >>> dataset = load_dataset("C-GAP-17")
        >>> ratios(dataset.info["config_type"])
          bulk_amo: 75.3%
        bulk_cryst:  8.8%
             dimer:  0.7%
          surf_amo: 15.2%
        >>> train, val, test = dataset.random_split(
        ...     [0.6, 0.2, 0.2],
        ...     keep_ratio="config_type"
        ... )
        >>> ratios(train.info["config_type"])
          bulk_amo: 75.3%
        bulk_cryst:  8.8%
                dimer:  0.7%
            surf_amo: 15.2%
        """

        if keep_ratio is None:
            return [
                AtomsDataset(split_structures)
                for split_structures in random_split(
                    self.structures, splits, seed
                )
            ]

        # the keep_ratio functionality is complicated if the user wants a
        # specific number of structures in each split. To side-step this,
        # we perform ratio-maintaining splits on the entire dataset, and then
        # randomly sample the correct number of structures from each split.
        if isinstance(splits[0], int):
            final_sizes = splits
            fractional_splits = [s / len(self) for s in splits]
        else:
            final_sizes = [int(s * len(self)) for s in splits]
            fractional_splits = splits

        # 1. separate into groups
        groups: dict[str, list[Atoms]] = defaultdict(list)
        for structure in self.structures:
            groups[structure.info[keep_ratio]].append(structure)

        # 2. split each group
        split_groups: dict[str, list[list[Atoms]]] = {
            key: random_split(value, fractional_splits, seed)
            for key, value in groups.items()
        }

        # 3. merge the splits
        final_splits: list[list[Atoms]] = [[] for _ in range(len(splits))]
        for group_splits in split_groups.values():
            for i, split in enumerate(group_splits):
                final_splits[i].extend(split)

        # 4. shuffle the splits
        def shuffle(thing):
            idx = np.random.RandomState(seed).permutation(len(thing))
            return [thing[i] for i in idx]

        final_splits = [shuffle(split) for split in final_splits]

        # 5. sample the correct number of structures from each split
        return [
            AtomsDataset(split[:size])
            for split, size in zip(final_splits, final_sizes)
        ]

    def k_fold_split(
        self,
        k: int = 5,
        fold: int = 0,
        shuffle: bool = True,
        seed: int = 42,
    ) -> tuple[AtomsDataset, AtomsDataset]:
        """
        Generate (an optionally shuffled) train/test split for cross-validation.

        Parameters
        ----------
        k
            The number of folds to use.
        fold
            The fold to use for testing.
        shuffle
            Whether to shuffle the dataset before splitting.
        seed
            The random seed to use for shuffling the dataset.

        Returns
        -------
        Tuple[Dataset, Dataset]
            The train and test datasets.

        Example
        -------

        .. code-block:: pycon
            :emphasize-lines: 2

            >>> for i in range(5):
            ...     train, test = dataset.k_fold_split(k=5, fold=i)
            ...     ...  # do something, e.g. train a model
        """

        if shuffle:
            idxs = np.random.RandomState(seed).permutation(len(self))
        else:
            idxs = np.arange(len(self))

        idxs = np.roll(idxs, fold * len(idxs) // k)
        n_test = len(self) // k
        train, test = idxs[:-n_test], idxs[-n_test:]

        return self[train], self[test]

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
        >>> dataset = load_dataset("C-GAP-17")
        The C-GAP-17 dataset is covered by the CC BY-NC-SA 4.0 license.
        Please cite the C-GAP-17 dataset if you use it in your work.

        Get the first structure in the dataset:

        >>> dataset[0]
        Atoms(symbols='C64', pbc=True, cell=[9.483, 9.483, 9.483], force=...)

        Create a new dataset with the first 10 structures:

        >>> dataset[:10]
        Dataset:
            structures: 10
            atoms: 640
            species:
                C: 100.00%
            properties:
                per atom: (force)
                per structure: (config_type, detailed_ct, split, energy)

        Create a new dataset of high energy structures using a mask
        (see :func:`~load_atoms.manipulations.filter_by` for a more convenient
        way to do this):

        >>> mask = dataset.info["energy"] / dataset.structure_sizes > -155
        >>> dataset[mask]
        Dataset:
            structures: 36
            atoms: 444
            species:
                C: 100.00%
            properties:
                per atom: (force)
                per structure: (config_type, detailed_ct, split, energy)
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


def usage_info(info: DatabaseEntry) -> str:
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
        description: DatabaseEntry,
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

        all_structures, info = backend.load_structures(dataset_id, root)

        # remove annoying automatic ASE calculators
        for structure in all_structures:
            structure.calc = None

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
    description: DatabaseEntry | None = None,
) -> str:
    name = description.name if description is not None else "Dataset"
    N = len(structures)
    number_atoms = sum([len(structure) for structure in structures])

    per_atom_properties = sorted(
        intersect(structure.arrays.keys() for structure in structures)
        - {"numbers", "positions"}
    )
    per_structure_properties = sorted(
        intersect(structure.info.keys() for structure in structures)
    )

    species = sorted(
        union(structure.get_chemical_symbols() for structure in structures)
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
