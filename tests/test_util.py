import pytest
from load_atoms.utils import LazyMapping, intersect, lpad, union


def test_intersection():
    assert intersect([[1, 2, 3], [2, 3, 4]]) == {2, 3}
    assert intersect(("hi", "hello")) == {"h"}


def test_union():
    assert union([[1, 2, 3], [2, 3, 4]]) == {1, 2, 3, 4}
    assert union(("hi", "hello")) == {"h", "e", "l", "o", "i"}


def test_pad():
    assert lpad("hi", 2) == " " * 2 + "hi"
    assert lpad("hi\nthere", 2) == "  hi\n  there"


def test_lazy_mapping():
    keys = [1, 2, 3]
    _calls = 0

    def loader(key):
        nonlocal _calls
        _calls += 1
        return key + 1

    mapping = LazyMapping(keys, loader)

    with pytest.raises(KeyError):
        mapping[4]

    assert 1 in mapping

    assert mapping[1] == 2
    assert _calls == 1

    mapping[1]
    assert _calls == 1
