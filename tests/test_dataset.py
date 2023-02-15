from ase import Atoms
from ase.io import read, write

from load_atoms import dataset
from load_atoms.database import DATASETS
from load_atoms.util import DATASETS_DIR

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


def is_valid(database_entry):
    assert hasattr(database_entry, "name")
    
    assert hasattr(database_entry, "filenames")
    assert len(database_entry.filenames) > 0

    for filename in database_entry.filenames:
        assert isinstance(filename, str)
        assert (DATASETS_DIR / filename).exists()
        first_structure = read(DATASETS_DIR / filename, index=0)
        assert isinstance(first_structure, Atoms)
    
    assert hasattr(database_entry, "description")
    assert isinstance(database_entry.description, str)


def test_database_entries():
    assert len(DATASETS) > 0
    
    for database_entry in DATASETS.values():
        is_valid(database_entry)

    