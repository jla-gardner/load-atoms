from ase import Atoms
from ase.io import read, write

from load_atoms import dataset
from load_atoms.database import _DESCRIPTOR_FILES

STRUCTURES = [Atoms("H2O"), Atoms("H2O2")]

def _is_water_dataset(ds):
    assert len(ds) == 2
    assert set(ds[0].symbols) == {"H", "O"}


def test_dataset_from_structures():
    ds = dataset(STRUCTURES)
    _is_water_dataset(ds)


def test_dataset_writeable_and_readable(tmp_path):
    ds = dataset(STRUCTURES)
    write(tmp_path / "test.xyz", ds)

    ds2 = dataset(read(tmp_path / "test.xyz", index=":"))
    _is_water_dataset(ds2)

    ds3 = dataset(tmp_path / "test.xyz")
    _is_water_dataset(ds3)


def test_can_load_from_id():
    print(_DESCRIPTOR_FILES)
    
    # pass root to avoid downloading the dataset
    structures = dataset("QM7", root="src/load_atoms/datasets") 
    assert len(structures) == 7165


    