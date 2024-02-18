# testing whether a visualisation works is difficult
# as a first stab, we can make sure that the function runs,
# and that the utility functions are working as expected

import pytest
from ase.build import molecule
from load_atoms import view
from load_atoms.visualisation import unique_variable_name


@pytest.mark.parametrize("show_bonds", [True, False])
def test_view(show_bonds):
    ethanol = molecule("CH3CH2OH")
    view(ethanol, show_bonds)

    ethanol.center(vacuum=5)
    ethanol.pbc = [True, True, True]
    view(ethanol, show_bonds)


def test_unique_variable_name():
    # ensure that the function returns a unique name
    # that is also a valid javascript variable name
    names = [unique_variable_name() for _ in range(10)]
    assert len(names) == len(set(names)), "Names should be unique"

    for name in names:
        assert name.isidentifier(), "Name should be a valid identifier"
        assert name[0].isalpha(), "Name should start with a letter"
        assert all(
            c.isalnum() or c == "_" for c in name
        ), "Name should only contain letters, numbers, or underscores"
