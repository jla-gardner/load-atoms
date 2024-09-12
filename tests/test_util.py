import pytest
from load_atoms.utils import (
    LazyMapping,
    freeze_dict,
    generate_checksum,
    intersect,
    k_fold_split,
    lpad,
    matches_checksum,
    random_split,
    split_keeping_ratio,
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

    # test error
    with pytest.raises(ValueError):
        random_split(x, [10, 10, 10])


def test_k_fold_split():
    x = list(range(10))

    a, b = k_fold_split(x, k=5, fold=0)
    assert a == list(range(8))
    assert b == [8, 9]

    a, b = k_fold_split(x, k=2, fold=1)
    assert a == list(range(5, 10))
    assert b == list(range(5))


def test_split_keeping_ratio():
    things = []
    for i in range(24):
        things.append(
            {
                "id": i,
                "group": 0 if i < 6 else 1 if i < 18 else 2,
            }
        )
    group_ids = [x["group"] for x in things]

    # random split
    a, b, c = split_keeping_ratio(
        things, group_ids, lambda x: random_split(x, [1 / 3, 1 / 3, 1 / 3])
    )
    assert len(a) == len(b) == len(c) == 8

    def proportions(things):
        counts = {0: 0, 1: 0, 2: 0}
        for x in things:
            counts[x["group"]] += 1
        max_count = max(counts.values())
        return {k: v / max_count for k, v in counts.items()}

    assert (
        proportions(a)
        == proportions(b)
        == proportions(c)
        == proportions(things)
    )

    # k-fold split
    x, y = split_keeping_ratio(
        things, group_ids, lambda x: k_fold_split(x, k=3, fold=0)
    )
    assert len(x) == 16
    assert len(y) == 8
    assert proportions(x) == proportions(y) == proportions(things)


def test_frozen_dict():
    d = dict(a=1, b=2, c=3)
    fd = freeze_dict(d)

    with pytest.raises(ValueError, match="read-only"):
        fd["a"] = 3
    assert fd["a"] == 1

    with pytest.raises(ValueError, match="read-only"):
        del fd["a"]
    assert "a" in fd

    with pytest.raises(ValueError, match="read-only"):
        fd.clear()
    assert len(fd) == 3

    with pytest.raises(ValueError, match="read-only"):
        fd.update({"a": 1})
    assert fd["a"] == 1

    with pytest.raises(ValueError, match="read-only"):
        fd.setdefault("a", 1)
    assert fd["a"] == 1

    with pytest.raises(ValueError, match="read-only"):
        fd.pop("a")
    assert fd["a"] == 1

    with pytest.raises(ValueError, match="read-only"):
        fd.popitem()
    assert fd["a"] == 1

    assert list(fd.keys()) == list(d.keys())
    assert list(fd.values()) == list(d.values())
    assert list(fd.items()) == list(d.items())
