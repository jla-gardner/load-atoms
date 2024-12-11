import ase.io
import numpy as np
import pytest
from ase import Atoms
from ase.calculators.singlepoint import SinglePointCalculator
from load_atoms import load_dataset
from load_atoms.utils import remove_calculator

from .setup import DATABASE_ROOT


def test_remove_calculator():
    structures = ase.io.read(
        DATABASE_ROOT / "C-GAP-17" / "C-GAP-17.extxyz",
        index=":",
    )
    assert isinstance(structures, list)

    # test ase.io.read behaviour
    assert isinstance(structures[0].calc, SinglePointCalculator)
    assert "energy" in structures[0].calc.results
    assert "energy" not in structures[0].info
    assert "forces" not in structures[0].arrays

    # test remove_calculator
    remove_calculator(structures[0])
    assert structures[0].calc is None
    assert "energy" in structures[0].info
    assert "forces" in structures[0].arrays

    # test load_dataset behaviour
    dataset = load_dataset(DATABASE_ROOT / "C-GAP-17" / "C-GAP-17.extxyz")
    assert dataset[0].calc is None
    assert "energy" in dataset.info
    assert dataset.info["energy"][0] == structures[0].info["energy"]
    assert "forces" in dataset.arrays

    # test clash
    atoms = Atoms("H2O")
    atoms.calc = SinglePointCalculator(atoms, energy=1.0)
    atoms.info["energy"] = 2.0

    with pytest.warns(UserWarning, match='different values for "energy"'):
        remove_calculator(atoms)

    assert atoms.calc is None
    assert atoms.info["energy"] == 2.0


def test_stress_conversion(tmp_path):
    stress = np.random.rand(3, 3)
    stress += stress.T  # make symmetric

    atoms = Atoms("Cu", cell=np.eye(3) * 5)
    atoms.info["stress"] = stress
    atoms.info["energy"] = np.random.rand()

    ase.io.write(tmp_path / "test.xyz", atoms)
    atoms2 = ase.io.read(tmp_path / "test.xyz")
    assert isinstance(atoms2, Atoms)
    # check ase conversion strangeness
    assert atoms2.calc is not None

    # stress is converted to voigt
    stress2 = atoms2.calc.get_stress()
    assert stress2.shape == (6,)

    atoms2.info["stress"] = stress
    assert atoms2.info["stress"].shape == (3, 3)
    with pytest.warns(UserWarning, match='different values for "stress"'):
        remove_calculator(atoms2)
    assert np.allclose(atoms2.info["stress"], stress)
