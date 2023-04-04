from ase import Atoms

from load_atoms.manipulations import cross_validate_split, filter_by

structures = [
    Atoms("H2O", info=dict(name="water")),
    Atoms("H2O2", info=dict(name="hydrogen peroxide")),
    Atoms("CH4", info=dict(name="methane")),
]


def test_filter_by():
    filtered = filter_by(
        structures,
        lambda structure: len(structure) >= 4,
    )
    assert len(filtered) == 2, "The filtered dataset should contain two structures"

    filtered = filter_by(
        structures,
        name="water",
    )
    assert len(filtered) == 1, "The filtered dataset should contain one structure"


def test_cv():
    train, test = cross_validate_split(structures, fold=1, folds=3)
    assert len(train) == 2, "The train dataset should contain two structures"
    assert len(test) == 1, "The test dataset should contain one structure"
