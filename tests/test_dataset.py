from pathlib import Path

import pytest
from ase import Atoms
from ase.io import read, write

from load_atoms import dataset
from load_atoms.dataset import Dataset, summarise_dataset

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


def test_slice():
    ds = dataset(STRUCTURES)

    structure = ds[0]
    assert isinstance(structure, Atoms), "Indexing should return an Atoms object"
    assert structure is STRUCTURES[0], "Indexing should return the same structure"

    sub_dataset = ds[1:]
    assert isinstance(sub_dataset, Dataset), "Slicing should return a dataset"
    assert (
        len(sub_dataset) == 1
    ), "Slicing should return the correct number of structures"


def test_can_load_from_id():
    # pass root to avoid downloading the dataset
    structures = dataset("QM7", root="src/load_atoms/datasets")
    assert len(structures) == 7165

    with pytest.raises(ValueError, match="is not known."):
        dataset("made_up_dataset")


def test_summarise():
    ds = dataset(STRUCTURES)
    summary = summarise_dataset(ds)
    assert "Dataset" in summary, "The summary should contain the dataset name"

    ds = dataset("C-GAP-17", root="src/load_atoms/datasets")
    summary = summarise_dataset(ds)
    assert "energy" in summary, "The summary should contain the property names"


def test_useful_error_message():
    with pytest.raises(
        TypeError,
        match="Please provide a string, a list of structures, or a path to a file.",
    ):
        dataset(1)

    with pytest.raises(
        ValueError,
        match="The provided path does not exist.",
    ):
        dataset(Path("made_up_file.xyz"))
