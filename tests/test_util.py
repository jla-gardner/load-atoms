import pytest
from load_atoms.utils import (
    LazyMapping,
    generate_checksum,
    intersect,
    matches_checksum,
    union,
)


def test_matches_contents(tmp_path):
    """
    Test that check_file_contents returns True if the contents of a file
    match the given hash.
    """

    fake_file = tmp_path / "file.txt"
    fake_file.write_text("fake file")

    correct_hash = generate_checksum(fake_file)
    incorrect_hash = "0" * 12

    assert matches_checksum(fake_file, correct_hash)
    assert not matches_checksum(fake_file, incorrect_hash)
    assert not matches_checksum(fake_file, correct_hash[:-1])


def test_intersection():
    assert intersect([[1, 2, 3], [2, 3, 4]]) == {2, 3}
    assert intersect(("hi", "hello")) == {"h"}


def test_union():
    assert union([[1, 2, 3], [2, 3, 4]]) == {1, 2, 3, 4}
    assert union(("hi", "hello")) == {"h", "e", "l", "o", "i"}


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
