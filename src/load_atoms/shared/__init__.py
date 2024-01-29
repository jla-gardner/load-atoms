from __future__ import annotations

from typing import Callable, Generic, Iterable, Sequence, TypeVar

BASE_REMOTE_URL = "https://github.com/jla-gardner/load-atoms/raw/main/database/"
FRONTEND_URL = "https://jla-gardner.github.io/load-atoms/datasets/"


class UnknownDatasetException(Exception):
    def __init__(self, dataset_id):
        super().__init__(f"Unknown dataset: {dataset_id}")


def union(things: Iterable[Iterable]):
    """Get the set union of a list of iterables."""
    return set.union(*map(set, things))


def intersect(things: Iterable[Iterable]):
    """Get the set intersection of a list of iterables."""
    return set.intersection(*map(set, things))


def lpad(s, indent=4):
    return "\n".join(" " * indent + line for line in s.splitlines())


def frontend_url(dataset_info):
    """Get the URL for a dataset's information page."""
    return FRONTEND_URL + dataset_info.name + ".html"


T = TypeVar("T")
Y = TypeVar("Y")


class LazyMapping(Generic[T, Y]):
    """
    A mapping that lazily loads its values.

    Parameters
    ----------
    keys
        The keys of the mapping.
    loader
        A function that takes a key and returns a value.
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
