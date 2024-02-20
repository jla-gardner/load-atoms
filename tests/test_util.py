import pytest
from load_atoms.utils import (
    LazyMapping,
    generate_checksum,
    intersect,
    lpad,
    matches_checksum,
    random_split,
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
    assert intersect([]) == set()


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


def test_lpad():
    # check multi-line strings
    s = """\
hello
world"""
    assert (
        lpad(s)
        == """\
    hello
    world"""
    )

    # test custom sep
    assert lpad("hi", 3, fill=":") == ":::hi"


def test_random_split():
    x = list(range(10))

    # test floats
    a, b = random_split(x, [0.5, 0.5])
    assert len(a) == len(b) == 5
    assert len(set(a) & set(b)) == 0, "splits should not overlap"

    # test ints
    a, b = random_split(x, [3, 3])
    assert len(a) == len(b) == 3
    assert len(set(a) & set(b)) == 0, "splits should not overlap"
