from pathlib import Path

import numpy as np
import pytest
from ase import Atoms
from ase.io import read, write
from load_atoms import dataset
from load_atoms.dataset import AtomsDataset, summarise_dataset
from load_atoms.utils import UnknownDatasetException

STRUCTURES = [Atoms("H2O"), Atoms("H2O2")]


def _is_water_dataset(ds):
    assert len(ds) == 2
    assert set(ds[0].symbols) == {"H", "O"}


def test_dataset_from_structures():
    ds = dataset(STRUCTURES)
    _is_water_dataset(ds)


def test_dataset_writeable_and_readable(tmp_path):
    ds = dataset(STRUCTURES)
    write(tmp_path / "test.xyz", ds)  # type: ignore

    ds2 = dataset(read(tmp_path / "test.xyz", index=":"))  # type: ignore
    _is_water_dataset(ds2)

    ds3 = dataset(tmp_path / "test.xyz")
    _is_water_dataset(ds3)


@pytest.mark.filterwarnings("ignore:Creating a dataset with a single structure")
def test_indexing():
    ds = dataset(STRUCTURES)

    structure = ds[0]
    assert isinstance(
        structure, Atoms
    ), "Indexing should return an Atoms object"
    assert (
        structure is STRUCTURES[0]
    ), "Indexing should return the same structure"

    sub_dataset = ds[1:]
    assert isinstance(
        sub_dataset, AtomsDataset
    ), "Slicing should return a dataset"
    assert (
        len(sub_dataset) == 1
    ), "Slicing should return the correct number of structures"

    indices = np.array([0, 1, 0, 1])
    sub_dataset = ds[indices]
    assert isinstance(
        sub_dataset, AtomsDataset
    ), "Indexing should return a dataset"
    assert (
        len(sub_dataset) == 4
    ), "Indexing should return the correct number of structures"

    indices = np.array([True, False])
    sub_dataset = ds[indices]
    assert isinstance(
        sub_dataset, AtomsDataset
    ), "Indexing should return a dataset"
    assert (
        len(sub_dataset) == 1
    ), "Indexing should return the correct number of structures"

    indices = [0, 1, 1]
    sub_dataset = ds[indices]
    assert isinstance(
        sub_dataset, AtomsDataset
    ), "Indexing should return a dataset"
    assert (
        len(sub_dataset) == 3
    ), "Indexing should return the correct number of structures"


def test_can_load_from_id():
    # don't pass a root to mimic the default behaviour
    structures = dataset("C-GAP-17")
    assert len(structures) == 4530

    with pytest.raises(UnknownDatasetException):
        dataset("made_up_dataset")


def test_summarise():
    ds = dataset(STRUCTURES)
    summary = summarise_dataset(ds)
    assert "Dataset" in summary, "The summary should contain the dataset name"

    ds = dataset("C-GAP-17")
    summary = repr(ds)
    assert "energy" in summary, "The summary should contain the property names"


def test_useful_error_message():
    with pytest.raises(
        TypeError,
        match="provide a string, a list of structures, or a path to a file.",
    ):
        dataset(1)  # type: ignore

    with pytest.raises(
        ValueError,
        match="The provided path does not exist.",
    ):
        dataset(Path("made_up_file.xyz"))


def test_useful_warning(tmp_path):
    structure = Atoms("H2O")
    write(tmp_path / "test.xyz", structure)  # type: ignore

    with pytest.warns(
        UserWarning,
        match="single structure",
    ):
        dataset(tmp_path / "test.xyz")


def tets_info_and_arrays():
    ds = dataset("QM7")

    assert "energy" in ds.info
    assert isinstance(ds.info["energy"], np.ndarray)

    assert "positions" in ds.arrays
    assert ds.arrays["positions"].shape[-1] == 3
