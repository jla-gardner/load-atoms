from load_atoms.util import intersection, union


def test_intersection():
    assert intersection([[1, 2, 3], [2, 3, 4]]) == {2, 3}
    assert intersection(("hi", "hello")) == {"h"}


def test_union():
    assert union([[1, 2, 3], [2, 3, 4]]) == {1, 2, 3, 4}
    assert union(("hi", "hello")) == {"h", "e", "l", "o", "i"}
