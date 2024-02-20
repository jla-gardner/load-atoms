from __future__ import annotations

import hashlib
import string
from collections import defaultdict
from pathlib import Path
from typing import Callable, Generic, Iterable, Sequence, TypeVar

import numpy as np

FRONTEND_URL = "https://jla-gardner.github.io/load-atoms/datasets/"
BASE_REMOTE_URL = "https://github.com/jla-gardner/load-atoms/raw/main/database/"


def generate_checksum(file_path: Path | str) -> str:
    """Generate a checksum for a file."""

    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)

    return sha256_hash.hexdigest()[:12]


def valid_checksum(hash: str) -> bool:
    """Check if a hash is valid."""
    if len(hash) != 12:
        return False
    return all(c in string.hexdigits for c in hash)


def matches_checksum(file_path: Path, hash: str) -> bool:
    """Check if a file matches a given hash."""
    return generate_checksum(file_path) == hash


T = TypeVar("T")
Y = TypeVar("Y")
G = TypeVar("G")


class LazyMapping(Generic[T, Y]):
    """
    A mapping that lazily loads its values.

    Concretely, the first time a key is accessed, the loader function is called
    to get the value for that key. Subsequent accesses to the same key will
    return the same value without calling the loader function again.

    Parameters
    ----------
    keys: Sequence[T]
        The keys of the mapping.
    loader: Callable[[T], Y]
        A function that takes a key and returns a value.

    Examples
    --------

    >>> def loader(key):
    ...     print(f"Loading value for key={key}")
    ...     return key * 2
    ...
    >>> mapping = LazyMapping([1, 2, 3], loader)
    >>> mapping[3]
    Loading value for key=3
    6
    >>> mapping[3]
    6
    >>> 1 in mapping
    True
    >>> 4 in mapping
    False
    """

    def __init__(
        self,
        keys: Sequence[T],
        loader: Callable[[T], Y],
    ):
        self.keys = keys
        self.loader = loader
        self._mapping = {}

    def __getitem__(self, key: T) -> Y:
        if key not in self.keys:
            raise KeyError(key)
        if key not in self._mapping:
            self._mapping[key] = self.loader(key)
        return self._mapping[key]

    def __contains__(self, key: T):
        return key in self.keys

    def __repr__(self) -> str:
        return f"LazyMapping(keys={self.keys})"


def frontend_url(dataset_info):
    """Get the URL for a dataset's information page."""
    return FRONTEND_URL + dataset_info.name + ".html"


class UnknownDatasetException(Exception):
    def __init__(self, dataset_id):
        super().__init__(f"Unknown dataset: {dataset_id}")


def union(things: Iterable[Iterable]):
    """Get the set union of a list of iterables."""
    return set.union(*map(set, things), set())


def intersect(things: Iterable[Iterable]):
    """Get the set intersection of a list of iterables."""
    sets = list(map(set, things))
    if not sets:
        return set()
    return set.intersection(*sets)


def lpad(thing: str, length: int = 4, fill: str = " "):
    """Left pad a string with a given fill character."""
    sep = f"{fill * length}"
    return sep + thing.replace("\n", f"\n{sep}")


def random_split(
    things: list[T],
    splits: list[int] | list[float],
    seed: int = 0,
) -> list[list[T]]:
    """Split a list into random chunks of given sizes."""

    if isinstance(splits[0], float):
        splits = [int(s * len(things)) for s in splits]
    if sum(splits) > len(things):
        raise ValueError(
            "The sum of the splits cannot exceed the dataset size."
        )

    cumulative_sum = np.cumsum(splits)

    idxs = np.random.RandomState(seed).permutation(len(things))
    return [
        [things[x] for x in idxs[i:j]]
        for i, j in zip([0, *cumulative_sum], cumulative_sum)
    ]


def k_fold_split(
    things: list[T],
    k: int,
    fold: int,
) -> tuple[list[T], list[T]]:
    assert 0 <= fold < k

    idxs = np.arange(len(things))
    idxs = np.roll(idxs, fold * len(things) // k)
    n_test = len(things) // k
    train, test = idxs[:-n_test], idxs[-n_test:]
    return [things[i] for i in train], [things[i] for i in test]


def split_keeping_ratio(
    things_to_split: list[T],
    group_ids: list[G],
    splitting_function: Callable[[list[T]], Sequence[list[T]]],
):
    assert len(things_to_split) == len(group_ids)

    # 1. separate into groups
    groups: dict[G, list[T]] = defaultdict(list)
    for thing, group_id in zip(things_to_split, group_ids):
        groups[group_id].append(thing)

    # 2. split each group
    splits_by_group: dict[G, Sequence[list[T]]] = {
        key: splitting_function(value) for key, value in groups.items()
    }

    # 3. merge the splits, thus keeping the ratio
    n_splits = len(splits_by_group[list(groups.keys())[0]])
    final_splits: list[list[T]] = [[] for _ in range(n_splits)]
    for group_splits in splits_by_group.values():
        for i, split in enumerate(group_splits):
            final_splits[i].extend(split)

    return final_splits
