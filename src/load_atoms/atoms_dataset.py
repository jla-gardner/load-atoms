from __future__ import annotations

import pickle
import warnings
from abc import ABC, abstractmethod
from dataclasses import dataclass
from functools import partial
from pathlib import Path
from typing import (
    Any,
    Callable,
    Iterable,
    Iterator,
    Literal,
    Mapping,
    Sequence,
    TypeVar,
    overload,
)

import ase
import lmdb
import numpy as np
from ase import Atoms
from typing_extensions import override
from yaml import dump

from .database import DatabaseEntry
from .utils import (
    LazyMapping,
    choose_n,
    intersect,
    k_fold_split,
    random_split,
    split_keeping_ratio,
    union,
)

T = TypeVar("T", bound="AtomsDataset")


class AtomsDataset(ABC, Sequence[Atoms]):
    """
    An abstract base class for datasets of :class:`ase.Atoms` objects.

    This class provides a common interface for interacting with datasets of
    atomic structures, abstracting over the underlying storage mechanism.
    """

    def __init__(self, description: DatabaseEntry | None = None):
        self.description = description

    @property
    @abstractmethod
    def structure_sizes(self) -> np.ndarray:
        pass

    @abstractmethod
    def __len__(self) -> int:
        pass

    @overload
    @abstractmethod
    def __getitem__(self, index: int) -> Atoms:
        ...

    @overload
    @abstractmethod
    def __getitem__(self: T, index: list[int] | np.ndarray | slice) -> T:
        ...

    @abstractmethod
    def __getitem__(
        self: T, index: int | list[int] | np.ndarray | slice
    ) -> Atoms | T:
        ...

    @abstractmethod
    def __iter__(self) -> Iterator[ase.Atoms]:
        pass

    @abstractmethod
    def __repr__(self) -> str:
        pass

    @property
    @abstractmethod
    def info(self) -> Mapping[str, Any]:
        pass

    @property
    @abstractmethod
    def arrays(self) -> Mapping[str, np.ndarray]:
        pass

    @classmethod
    @abstractmethod
    def save(
        cls,
        path: Path,
        structures: Iterable[Atoms],
        description: DatabaseEntry | None = None,
    ):
        ...

    @classmethod
    @abstractmethod
    def load(cls: type[T], path: Path) -> T:
        pass

    # concrete methods

    def __contains__(self, item: Any) -> bool:
        return any(item == other for other in self)

    @property
    def n_atoms(self) -> int:
        return int(self.structure_sizes.sum())

    def filter_by(
        self: T,
        *functions: Callable[[ase.Atoms], bool],
        **info_kwargs: Any,
    ) -> T:
        """
        Return a new dataset containing only the structures that match the
        given criteria.

        Parameters
        ----------
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

        index = [i for i, structure in enumerate(self) if the_filter(structure)]
        return self[index]

    def random_split(
        self: T,
        splits: Sequence[float] | Sequence[int],
        seed: int = 42,
        keep_ratio: str | None = None,
    ) -> list[T]:
        r"""
        Randomly split the dataset into multiple, disjoint parts.

        Parameters
        ----------
        splits
            The number of structures to put in each split.
            If a list of :class:`float`\ s, the splits will be
            calculated as a fraction of the dataset size.
        seed
            The random seed to use for shuffling the dataset.
        keep_ratio
            If not :code:`None`, splits will be generated to maintain the
            ratio of structures in each split with the specified :code:`.info`
            value.

        Returns
        -------
        list[T]
            A list of new datasets, each containing a subset of the original

        Examples
        --------
        Split a :code:`dataset` into 80% training and 20% test sets:

        >>> train, test = dataset.random_split([0.8, 0.2])

        Split a :code:`dataset` into 3 parts:

        >>> train, val, test = dataset.random_split([1_000, 100, 100])

        Maintain the ratio of :code:`config_type` values in each split:

        .. code-block:: pycon
            :emphasize-lines: 16-19

            >>> from load_atoms import load_dataset
            >>> import numpy as np
            >>> # helper function
            >>> def ratios(thing):
            ...     values, counts = np.unique(thing, return_counts=True)
            ...     max_len = max(len(str(v)) for v in values)
            ...     for v, c in zip(values, counts / counts.sum()):
            ...         print(f"{v:>{max_len}}: {c:>6.2%}")
            ...
            >>> dataset = load_dataset("C-GAP-17")
            >>> ratios(dataset.info["config_type"])
              bulk_amo: 75.28%
            bulk_cryst:  8.83%
                 dimer:  0.66%
              surf_amo: 15.23%
            >>> train, val, test = dataset.random_split(
            ...     [0.6, 0.2, 0.2],
            ...     keep_ratio="config_type"
            ... )
            >>> ratios(train.info["config_type"])
              bulk_amo: 75.28%
            bulk_cryst:  8.83%
                 dimer:  0.66%
              surf_amo: 15.23%
        """

        if keep_ratio is None:
            return [
                self[split]
                for split in random_split(range(len(self)), splits, seed)
            ]

        if keep_ratio not in self.info:
            raise KeyError(
                f"Unknown key {keep_ratio}. "
                "Available keys are: " + ", ".join(self.info.keys())
            )

        if isinstance(splits[0], int):
            final_sizes: list[int] = splits  # type: ignore
        else:
            final_sizes = [int(s * len(self)) for s in splits]

        normalised_fractional_splits = [s / sum(splits) for s in splits]

        split_idxs = split_keeping_ratio(
            range(len(self)),
            group_ids=self.info[keep_ratio],
            splitting_function=partial(
                random_split, seed=seed, splits=normalised_fractional_splits
            ),
        )

        return [
            self[choose_n(split, size, seed)]
            for split, size in zip(split_idxs, final_sizes)
        ]

    def k_fold_split(
        self: T,
        k: int = 5,
        fold: int = 0,
        shuffle: bool = True,
        seed: int = 42,
        keep_ratio: str | None = None,
    ) -> tuple[T, T]:
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
        keep_ratio
            If not :code:`None`, splits will be generated to maintain the
            ratio of structures in each split with the specified :code:`.info`
            value.

        Returns
        -------
        Tuple[Dataset, Dataset]
            The train and test datasets.

        Example
        -------

        Basic usage:

        .. code-block:: pycon
            :emphasize-lines: 2

            >>> for i in range(5):
            ...     train, test = dataset.k_fold_split(k=5, fold=i)
            ...     ...  # do something, e.g. train a model

        Maintain the ratio of :code:`config_type` values in each split
        (see also :func:`~load_atoms.AtomsDataset.random_split` for a more
        detailed example of this feature):

        .. code-block:: pycon

            >>> train, test = dataset.k_fold_split(
            ...     k=5, fold=0, keep_ratio="config_type"
            ... )

        """

        if k < 2:
            raise ValueError("k must be at least 2")

        fold = fold % k

        if shuffle:
            idxs = np.random.RandomState(seed).permutation(len(self))
        else:
            idxs = np.arange(len(self))

        if keep_ratio is None:
            train_idxs, test_idxs = k_fold_split(idxs.tolist(), k, fold)
        else:
            if keep_ratio not in self.info:
                raise KeyError(
                    f"Unknown key {keep_ratio}. "
                    "Available keys are: " + ", ".join(self.info.keys())
                )
            if not shuffle:
                raise ValueError(
                    "Keep ratio splits are only supported when shuffling."
                )

            group_ids = self.info[keep_ratio][idxs]
            train_idxs, test_idxs = split_keeping_ratio(
                idxs.tolist(), group_ids, partial(k_fold_split, k=k, fold=fold)
            )

        return self[train_idxs], self[test_idxs]


class InMemoryAtomsDataset(AtomsDataset):
    """An in-memory implementation of AtomsDataset."""

    def __init__(
        self,
        structures: list[ase.Atoms],
        description: DatabaseEntry | None = None,
    ):
        super().__init__(description)

        if len(structures) == 1:
            warnings.warn(
                "Creating a dataset with a single structure. "
                "Typically, datasets contain multiple structures - "
                "did you mean to do this?",
                stacklevel=2,
            )

        self._structures = structures

        keys, loader = _get_info_loader(structures)
        self._info: LazyMapping[str, Any] = LazyMapping(keys, loader)

        keys, loader = _get_arrays_loader(structures)
        self._arrays: LazyMapping[str, np.ndarray] = LazyMapping(keys, loader)

    @property
    @override
    def info(self) -> LazyMapping[str, Any]:
        return self._info

    @property
    @override
    def arrays(self) -> LazyMapping[str, np.ndarray]:
        return self._arrays

    @property
    @override
    def structure_sizes(self) -> np.ndarray:
        return np.array([len(s) for s in self._structures])

    @override
    def __len__(self) -> int:
        return len(self._structures)

    @override
    def __getitem__(  # type: ignore
        self,
        index: int | list[int] | np.ndarray | slice,
    ) -> Atoms | InMemoryAtomsDataset:
        if isinstance(index, slice):
            return InMemoryAtomsDataset(
                self._structures[index], self.description
            )
        if hasattr(index, "__iter__"):
            assert not isinstance(index, int)
            if isinstance(index, np.ndarray):
                to_keep = np.arange(len(self))[index]
                return InMemoryAtomsDataset(
                    [self._structures[i] for i in to_keep], self.description
                )
            return InMemoryAtomsDataset(
                [self._structures[i] for i in index], self.description
            )

        index = int(index)  # type: ignore
        return self._structures[index]

    @override
    def __iter__(self) -> Iterator[ase.Atoms]:
        return iter(self._structures)

    @override
    def __repr__(self) -> str:
        return summarise_dataset(self._structures, self.description)

    @override
    @classmethod
    def save(
        cls,
        path: Path,
        structures: Iterable[Atoms],
        description: DatabaseEntry | None = None,
    ):
        path.parent.mkdir(parents=True, exist_ok=True)
        to_save = {
            "structures": list(structures),
            "description": description,
        }
        with open(path, "wb") as f:
            pickle.dump(to_save, f)

    @classmethod
    @override
    def load(cls, path: Path) -> InMemoryAtomsDataset:
        with open(path, "rb") as f:
            data = pickle.load(f)
        return cls(**data)


@dataclass
class LmdbMetadata:
    structure_sizes: np.ndarray
    per_atom_properties: list[str]
    per_structure_properties: list[str]


class LmdbAtomsDataset(AtomsDataset):
    """An LMDB-backed implementation of AtomsDataset."""

    def __init__(self, path: Path, idx_subset: np.ndarray | None = None):
        self.path = path

        # setup lmdb environment, and keep a transaction open for the lifetime
        # of the dataset (to enable fast reads)
        self.env = lmdb.open(
            str(path), readonly=True, lock=False, map_async=True
        )
        self.txn = self.env.begin(write=False)

        self.metadata: LmdbMetadata = pickle.loads(
            self.txn.get("metadata".encode("ascii"))
        )
        self.idx_subset = (
            idx_subset
            if idx_subset is not None
            else np.arange(len(self.metadata.structure_sizes))
        )

        self._info: LazyMapping[str, Any] = LazyMapping(
            self.metadata.per_structure_properties,
            lambda key: np.array([structure.info[key] for structure in self]),
        )
        self._arrays: LazyMapping[str, np.ndarray] = LazyMapping(
            self.metadata.per_atom_properties,
            lambda key: np.concatenate(
                [structure.arrays[key] for structure in self]
            ),
        )

    def close(self):
        self.txn.close()
        self.env.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def _get_structure_by_idx(self, idx: int) -> Atoms:
        pickled_data = self.txn.get(f"{idx}".encode("ascii"))
        return pickle.loads(pickled_data)

    @property
    @override
    def structure_sizes(self) -> np.ndarray:
        sizes = self.metadata.structure_sizes
        if self.idx_subset is not None:
            return sizes[self.idx_subset]
        return sizes

    @override
    def __len__(self) -> int:
        return len(self.structure_sizes)

    @override
    def __getitem__(  # type: ignore
        self,
        index: int | list[int] | np.ndarray | slice,
    ) -> Atoms | LmdbAtomsDataset:
        if isinstance(index, int):
            return self._get_structure_by_idx(index)
        else:
            return LmdbAtomsDataset(self.path, self.idx_subset[index])

    @override
    def __iter__(self) -> Iterator[ase.Atoms]:
        for idx in self.idx_subset:
            yield self._get_structure_by_idx(idx)

    @override
    def __repr__(self) -> str:
        return "TODO"

    @property
    @override
    def info(self) -> LazyMapping[str, Any]:
        return self._info

    @property
    @override
    def arrays(self) -> LazyMapping[str, np.ndarray]:
        return self._arrays

    @classmethod
    @override
    def load(cls, path: Path) -> LmdbAtomsDataset:
        return cls(path)

    @classmethod
    @override
    def save(
        cls,
        path: Path,
        structures: Iterable[Atoms],
        description: DatabaseEntry | None = None,
    ):
        path.mkdir(parents=True, exist_ok=True)

        one_TB = int(1e12)
        env = lmdb.open(str(path), map_size=one_TB)

        with env.begin(write=True) as txn:
            structure_sizes = []
            per_atom_properties = set()
            per_structure_properties = set()

            for idx, structure in enumerate(structures):
                # Save structure
                txn.put(f"{idx}".encode("ascii"), pickle.dumps(structure))

                # Update metadata
                structure_sizes.append(len(structure))
                per_atom_properties.update(
                    structure.arrays.keys() - {"numbers", "positions"}
                )
                per_structure_properties.update(structure.info.keys())

            # Save metadata
            metadata = LmdbMetadata(
                structure_sizes=np.array(structure_sizes),
                per_atom_properties=sorted(per_atom_properties),
                per_structure_properties=sorted(per_structure_properties),
            )
            txn.put("metadata".encode("ascii"), pickle.dumps(metadata))

            # Save description if provided
            if description:
                txn.put(
                    "description".encode("ascii"), pickle.dumps(description)
                )

        env.close()


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


def get_file_extension_and_dataset_class(
    format: Literal["lmdb", "memory"]
) -> tuple[str, type[AtomsDataset]]:
    return {
        "lmdb": (".lmdb", LmdbAtomsDataset),
        "memory": (".pkl", InMemoryAtomsDataset),
    }[format]
