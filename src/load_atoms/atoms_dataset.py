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
    overload,
)

import ase
import lmdb
import numpy as np
from ase import Atoms
from ase.data import chemical_symbols
from typing_extensions import Self, override
from yaml import dump

from .database import DatabaseEntry
from .utils import (
    LazyMapping,
    choose_n,
    freeze_dict,
    intersect,
    k_fold_split,
    random_split,
    split_keeping_ratio,
)


class AtomsDataset(ABC, Sequence[Atoms]):
    """
    An abstract base class for datasets of :class:`ase.Atoms` objects.

    This class provides a common interface for interacting with datasets of
    atomic structures, abstracting over the underlying storage mechanism.

    The two current concrete implementations are
    :class:`~load_atoms.atoms_dataset.InMemoryAtomsDataset`
    and :class:`~load_atoms.atoms_dataset.LmdbAtomsDataset`.
    """

    def __init__(self, description: DatabaseEntry | None = None):
        self.description = description

    @property
    @abstractmethod
    def structure_sizes(self) -> np.ndarray:
        """
        An array containing the number of atoms in each structure, such that:

        .. code-block:: python

            for idx, structure in enumerate(dataset):
                assert len(structure) == dataset.structure_sizes[idx]
        """

    @abstractmethod
    def __len__(self) -> int:
        """The number of structures in the dataset."""

    @overload
    def __getitem__(self, index: int) -> Atoms:
        ...

    @overload
    def __getitem__(
        self, index: list[int] | list[bool] | np.ndarray | slice
    ) -> Self:
        ...

    def __getitem__(  # type: ignore
        self,
        index: int | list[int] | np.ndarray | slice,
    ) -> Atoms | Self:
        r"""
        Get the structure(s) at the given index(es).

        If a single :class:`int` is provided, the corresponding structure is
        returned:

        .. code-block:: pycon

            >>> QM7 = load_dataset("QM7")
            >>> QM7[0]
            Atoms(symbols='CH4', pbc=False)

        If a :class:`slice` is provided, a new :class:`AtomsDataset` is returned
        containing the structures in the slice:

        .. code-block:: pycon

            >>> QM7[:5]
            Dataset:
                structures: 5
                atoms: 32
                species:
                    H: 68.75%
                    C: 28.12%
                    O: 3.12%
                properties:
                    per atom: ()
                    per structure: (energy)

        If a :class:`list` or :class:`numpy.ndarray` of :class:`int`\ s is
        provided, a new :class:`AtomsDataset` is returned containing the
        structures at the given indices:

        .. code-block:: pycon

            >>> len(QM7[[0, 2, 4]])
            3

        If a :class:`list` or :class:`numpy.ndarray` of :class:`bool`\ s is
        provided with the same length as the dataset, a new
        :class:`AtomsDataset` is returned containing the structures where the
        boolean is :code:`True`
        (see also :func:`~load_atoms.AtomsDataset.filter_by`):

        .. code-block:: pycon

            >>> bool_idx = [
            ...     len(s) > 10 for s in QM7
            ... ]
            >>> len(QM7[bool_idx]) == sum(bool_idx)
            True

        Parameters
        ----------
        index
            The index(es) to get the structure(s) at.
        """

        if isinstance(index, slice):
            idxs = range(len(self))[index]
            return self._index_subset(idxs)

        if isinstance(index, list):
            if all(isinstance(i, bool) for i in index):
                if len(index) != len(self):
                    raise ValueError(
                        "Boolean index list must be the same length as the "
                        "dataset."
                    )
                return self._index_subset([i for i, b in enumerate(index) if b])
            else:
                return self._index_subset(index)

        if isinstance(index, np.ndarray):
            return self._index_subset(np.arange(len(self))[index])

        index = int(index)
        return self._index_structure(index)

    def __iter__(self) -> Iterator[ase.Atoms]:
        for i in range(len(self)):
            yield self._index_structure(i)

    @abstractmethod
    def _index_structure(self, index: int) -> Atoms:
        """Get the structure at the given index."""

    @abstractmethod
    def _index_subset(self, idxs: Sequence[int]) -> Self:
        """Get a new dataset containing the structures at the given indices."""

    def __repr__(self) -> str:
        name = "Dataset" if not self.description else self.description.name
        per_atom_properties = (
            "("
            + ", ".join(
                sorted(
                    set(self.arrays.keys())
                    - {
                        "numbers",
                        "positions",
                    }
                )
            )
            + ")"
        )
        per_structure_properties = (
            "(" + ", ".join(sorted(self.info.keys())) + ")"
        )
        species_counts = self.species_counts()
        species_percentages = {
            symbol: f"{count / self.n_atoms:0.2%}"
            for symbol, count in sorted(
                species_counts.items(), key=lambda item: item[1], reverse=True
            )
        }

        return dump(
            {
                name: {
                    "structures": f"{len(self):,}",
                    "atoms": f"{self.n_atoms:,}",
                    "species": species_percentages,
                    "properties": {
                        "per atom": per_atom_properties,
                        "per structure": per_structure_properties,
                    },
                }
            },
            sort_keys=False,
            indent=4,
        )

    @property
    @abstractmethod
    def info(self) -> Mapping[str, Any]:
        r"""
        Get a mapping from keys that are shared across all structures'
        ``.info`` attributes to the concatenated corresponding values.

        The returned mapping conforms to:

        .. code-block:: python

            for key, value in dataset.info.items():
                for i, structure in enumerate(dataset):
                    assert structure.info[key] == value[i]
        """

    @property
    @abstractmethod
    def arrays(self) -> Mapping[str, np.ndarray]:
        """
        Get a mapping from each structure's :code:`.arrays` keys to arrays.

        The returned mapping conforms to:

        .. code-block:: python

            for key, value in dataset.arrays.items():
                assert value.shape[0] == dataset.n_atoms
                assert value == np.vstack(
                    [structure.arrays[key] for structure in dataset]
                )
        """

    @classmethod
    @abstractmethod
    def save(
        cls,
        path: Path,
        structures: Iterable[Atoms],
        description: DatabaseEntry | None = None,
    ):
        """
        Save the dataset to a file.

        Parameters
        ----------
        path
            The path to save the dataset to.
        structures
            The structures to save to the dataset.
        description
            The description of the dataset.
        """

    @classmethod
    @abstractmethod
    def load(cls, path: Path) -> Self:
        """
        Load the dataset from a file.

        Parameters
        ----------
        path
            The path to load the dataset from.
        """
        pass

    # concrete methods

    def species_counts(self) -> Mapping[str, int]:
        """
        Get the number of atoms of each species in the dataset.
        """
        return {
            chemical_symbols[species]: (self.arrays["numbers"] == species).sum()
            for species in np.unique(self.arrays["numbers"])
        }

    def __contains__(self, item: Any) -> bool:
        """
        Check if the dataset contains a structure.

        Warning: this method is not efficient for large datasets.
        """
        return any(item == other for other in self)

    @property
    def n_atoms(self) -> int:
        r"""
        The total number of atoms in the dataset.

        This is equivalent to the sum of the number of atoms in each structure.
        """
        return int(self.structure_sizes.sum())

    def filter_by(
        self,
        *functions: Callable[[ase.Atoms], bool],
        **info_kwargs: Any,
    ) -> Self:
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
        self,
        splits: Sequence[float] | Sequence[int],
        seed: int = 42,
        keep_ratio: str | None = None,
    ) -> list[Self]:
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
        list[Self]
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
        self,
        k: int = 5,
        fold: int = 0,
        shuffle: bool = True,
        seed: int = 42,
        keep_ratio: str | None = None,
    ) -> tuple[Self, Self]:
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
        Tuple[Self, Self]
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
    """
    An in-memory implementation of :class:`AtomsDataset`.

    Internally, this class wraps a :class:`list` of :class:`ase.Atoms` objects,
    all of which are stored in RAM. Suitable for small to moderately large
    datasets.
    """

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
        self._info = _get_info_mapping(structures)
        self._arrays = _get_arrays_mapping(structures)

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
    def _index_structure(self, index: int) -> Atoms:
        return self._structures[index]

    @override
    def _index_subset(self, idxs: Sequence[int]) -> InMemoryAtomsDataset:
        return InMemoryAtomsDataset([self._index_structure(i) for i in idxs])

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
    species_per_structure: list[dict[str, int]]
    per_atom_properties: list[str]
    per_structure_properties: list[str]


class LmdbAtomsDataset(AtomsDataset):
    r"""
    An LMDB-backed implementation of :class:`AtomsDataset`.

    Internally, this class wraps an :class:`lmdb.Environment` object, which
    stores the dataset in an LMDB database. Suitable for large datasets that
    cannot fit in memory. Accessing data from this dataset type is (marginally)
    slower than for :class:`InMemoryAtomsDataset`\ s, but allows for efficient
    processing of extremely large datasets that cannot otherwise fit in memory.

    .. warning::

        The :class:`ase.Atoms` objects in an LMDB dataset are read-only.
        Modifying the :code:`.info` or :code:`.arrays` of an :class:`ase.Atoms`
        object will have no effect, and will instead throw an error.
    """

    def __init__(self, path: Path, idx_subset: np.ndarray | None = None):
        self.path = path

        # setup lmdb environment, and keep a transaction open for the lifetime
        # of the dataset (to enable fast reads)
        self.env = lmdb.open(
            str(path), readonly=True, lock=False, map_async=True
        )
        self.txn = self.env.begin(write=False)

        super().__init__(
            description=pickle.loads(
                self.txn.get("description".encode("ascii"))
            )
        )

        self.metadata: LmdbMetadata = pickle.loads(
            self.txn.get("metadata".encode("ascii"))
        )
        self.idx_subset = (
            idx_subset
            if idx_subset is not None
            else np.arange(len(self.metadata.structure_sizes))
        )

        # TODO: add warnings to loaders about potential slowness
        self._info = _get_info_mapping(
            structures=self,
            keys=self.metadata.per_structure_properties,
            loader_warning=(
                "LmdbAtomsDatasets do not hold all structure properties in "
                "memory: accessing .info will be slow."
            ),
        )
        self._arrays = _get_arrays_mapping(
            structures=self,
            keys=self.metadata.per_atom_properties + ["numbers", "positions"],
            loader_warning=(
                "LmdbAtomsDatasets do not hold all per-atom properties in "
                "memory: accessing .arrays will be slow."
            ),
        )

    def close(self):
        self.txn.close()
        self.env.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def _index_structure(self, index: int) -> Atoms:
        index = self.idx_subset[index]
        pickled_data = self.txn.get(f"{index}".encode("ascii"))
        atoms = pickle.loads(pickled_data)
        error_msg = (
            "The Atoms objects in an LMDB dataset are read-only: "
            "modifying the {} of an Atoms object will have no effect."
        )
        atoms.info = freeze_dict(atoms.info, error_msg.format("info"))
        atoms.arrays = freeze_dict(atoms.arrays, error_msg.format("arrays"))
        return atoms

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
    def species_counts(self) -> Mapping[str, int]:
        to_sum: list[dict[str, int]] = []
        all_species: set[str] = set()

        for idx in self.idx_subset:
            species_count = self.metadata.species_per_structure[idx]
            to_sum.append(species_count)
            all_species.update(species_count.keys())

        summed = {symbol: 0 for symbol in all_species}
        for species_count in to_sum:
            for symbol, count in species_count.items():
                summed[symbol] += count
        return summed

    @override
    def __contains__(self, item: Any) -> bool:
        warnings.warn(
            "Checking if an LMDB dataset contains a structure is slow "
            "because it requires loading every structure into memory. "
            "Consider using a different dataset format if possible.",
            stacklevel=2,
        )
        return any(item == structure for structure in self)

    @override
    def _index_subset(self, idxs: Sequence[int]) -> LmdbAtomsDataset:
        return LmdbAtomsDataset(self.path, self.idx_subset[idxs])

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
            species_per_structure = []
            per_atom_properties: list[set[str]] = []
            per_structure_properties: list[set[str]] = []

            for idx, structure in enumerate(structures):
                # Save structure
                txn.put(f"{idx}".encode("ascii"), pickle.dumps(structure))

                # Update metadata
                structure_sizes.append(len(structure))
                species_per_structure.append(
                    {
                        chemical_symbols[Z]: (
                            structure.arrays["numbers"] == Z
                        ).sum()
                        for Z in np.unique(structure.arrays["numbers"])
                    }
                )
                per_atom_properties.append(
                    set(structure.arrays.keys()) - {"numbers", "positions"}
                )
                per_structure_properties.append(set(structure.info.keys()))

            # Save metadata
            metadata = LmdbMetadata(
                structure_sizes=np.array(structure_sizes),
                species_per_structure=species_per_structure,
                per_atom_properties=sorted(intersect(per_atom_properties)),
                per_structure_properties=sorted(
                    intersect(per_structure_properties)
                ),
            )
            txn.put("metadata".encode("ascii"), pickle.dumps(metadata))

            # Save description if provided
            if description:
                txn.put(
                    "description".encode("ascii"), pickle.dumps(description)
                )

        env.close()


def _get_info_mapping(
    structures: Iterable[Atoms],
    keys: list[str] | None = None,
    loader_warning: str | None = None,
) -> LazyMapping[str, np.ndarray]:
    if keys is None:
        keys = list(intersect(s.info.keys() for s in structures))

    def loader(key: str):
        if loader_warning is not None:
            warnings.warn(loader_warning, stacklevel=2)
        return np.array([s.info[key] for s in structures])

    return LazyMapping(keys, loader)


def _get_arrays_mapping(
    structures: Iterable[Atoms],
    keys: list[str] | None = None,
    loader_warning: str | None = None,
) -> LazyMapping[str, np.ndarray]:
    if keys is None:
        keys = list(intersect(s.arrays.keys() for s in structures))

    def loader(key: str):
        if loader_warning is not None:
            warnings.warn(loader_warning, stacklevel=2)
        return np.concatenate([s.arrays[key] for s in structures])

    return LazyMapping(keys, loader)


def summarise_dataset(
    structures: list[Atoms] | AtomsDataset,
    description: DatabaseEntry | None = None,
) -> str:
    if isinstance(structures, AtomsDataset):
        return str(structures)
    return str(InMemoryAtomsDataset(structures, description))


def get_file_extension_and_dataset_class(
    format: Literal["lmdb", "memory"]
) -> tuple[str, type[AtomsDataset]]:
    return {
        "lmdb": ("lmdb", LmdbAtomsDataset),
        "memory": ("pkl", InMemoryAtomsDataset),
    }[format]
