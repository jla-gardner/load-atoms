from ase import Atoms
from ase.io import read, write

from load_atoms import dataset

STRUCTURES = [Atoms("H2O"), Atoms("H2O2")]


def test_dataset_from_structures():
    ds = dataset(STRUCTURES)
    assert len(ds) == 2
    assert set(ds[0].symbols) == {"H", "O"}


def test_dataset_writeable_and_readable(tmp_path):
    ds = dataset(STRUCTURES)
    write(tmp_path / "test.xyz", ds)

    ds2 = dataset(read(tmp_path / "test.xyz", index=":"))

    assert len(ds2) == 2
    assert set(ds[0].symbols) == {"H", "O"}


    