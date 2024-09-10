from pathlib import Path

import numpy as np
import pytest
from ase import Atoms
from ase.io import read, write
from load_atoms import load_dataset
from load_atoms.atoms_dataset import AtomsDataset, summarise_dataset
from load_atoms.utils import UnknownDatasetException
from setup import TESTING_DIR

STRUCTURES = [Atoms("H2O"), Atoms("H2O2")]
GAP17 = load_dataset("C-GAP-17", root=TESTING_DIR)


def _is_water_dataset(dataset):
    assert len(dataset) == 2
    assert set(dataset[0].symbols) == {"H", "O"}


def test_dataset_from_structures():
    dataset = load_dataset(STRUCTURES)
    _is_water_dataset(dataset)


def test_dataset_writeable_and_readable(tmp_path):
    dataset = load_dataset(STRUCTURES)
    write(tmp_path / "test.xyz", dataset)  # type: ignore

    dataset2 = load_dataset(read(tmp_path / "test.xyz", index=":"))  # type: ignore
    _is_water_dataset(dataset2)

    dataset3 = load_dataset(tmp_path / "test.xyz")
    _is_water_dataset(dataset3)


@pytest.mark.filterwarnings("ignore:Creating a dataset with a single structure")
def test_indexing():
    dataset = load_dataset(STRUCTURES)

    structure = dataset[0]
    assert isinstance(
        structure, Atoms
    ), "Indexing should return an Atoms object"
    assert (
        structure is STRUCTURES[0]
    ), "Indexing should return the same structure"

    sub_dataset = dataset[1:]
    assert isinstance(
        sub_dataset, AtomsDataset
    ), "Slicing should return a dataset"
    assert (
        len(sub_dataset) == 1
    ), "Slicing should return the correct number of structures"

    indices = np.array([0, 1, 0, 1])
    sub_dataset = dataset[indices]
    assert isinstance(
        sub_dataset, AtomsDataset
    ), "Indexing should return a dataset"
    assert (
        len(sub_dataset) == 4
    ), "Indexing should return the correct number of structures"

    indices = np.array([True, False])
    sub_dataset = dataset[indices]
    assert isinstance(
        sub_dataset, AtomsDataset
    ), "Indexing should return a dataset"
    assert (
        len(sub_dataset) == 1
    ), "Indexing should return the correct number of structures"

    indices = [0, 1, 1]
    sub_dataset = dataset[indices]
    assert isinstance(
        sub_dataset, AtomsDataset
    ), "Indexing should return a dataset"
    assert (
        len(sub_dataset) == 3
    ), "Indexing should return the correct number of structures"


def test_can_load_from_id(tmp_path):
    assert len(GAP17) == 4530

    with pytest.raises(UnknownDatasetException):
        load_dataset("made_up_dataset", root=tmp_path)


def test_summarise():
    dataset = load_dataset(STRUCTURES)
    summary = summarise_dataset(dataset)
    assert "Dataset" in summary, "The summary should contain the dataset name"

    summary = repr(GAP17)
    assert "energy" in summary, "The summary should contain the property names"


def test_useful_error_message():
    with pytest.raises(
        TypeError,
        match="provide a string, a list of structures, or a path to a file.",
    ):
        load_dataset(1)  # type: ignore

    with pytest.raises(
        ValueError,
        match="The provided path does not exist.",
    ):
        load_dataset(Path("made_up_file.xyz"))


def test_useful_warning(tmp_path):
    structure = Atoms("H2O")
    write(tmp_path / "test.xyz", structure)  # type: ignore

    with pytest.warns(
        UserWarning,
        match="single structure",
    ):
        load_dataset(tmp_path / "test.xyz")


def test_info_and_arrays():
    assert "energy" in GAP17.info
    assert isinstance(GAP17.info["energy"], np.ndarray)

    assert "positions" in GAP17.arrays
    assert GAP17.arrays["positions"].shape[-1] == 3


def test_properties():
    dataset = load_dataset(STRUCTURES)

    assert len(dataset) == 2
    assert dataset.n_atoms == 7
    assert (dataset.structure_sizes == [3, 4]).all()


def _get_proportion(config_type, dataset):
    return np.sum(dataset.info["config_type"] == config_type) / len(dataset)


def test_random_split():
    # request integer splits
    train, test = GAP17.random_split([100, 50])
    assert len(train) == 100
    assert len(test) == 50

    # request float splits
    n = len(GAP17)
    a, b, c = GAP17.random_split([0.5, 0.25, 0.25])
    assert len(a) == n // 2
    assert len(b) in [n // 4, n // 4 + 1]
    assert len(c) in [n // 4, n // 4 + 1]

    # test keep ratio
    assert "config_type" in GAP17.info
    assert "bulk_amo" in GAP17.info["config_type"]

    # ... with floats
    a, b = GAP17.random_split([0.5, 0.5], keep_ratio="config_type")
    assert len(a) + len(b) == len(GAP17)
    assert np.isclose(
        _get_proportion("bulk_amo", a), _get_proportion("bulk_amo", GAP17)
    )

    # ... with ints
    a, b = GAP17.random_split([500, 500], keep_ratio="config_type")
    assert np.isclose(
        _get_proportion("bulk_amo", a),
        _get_proportion("bulk_amo", GAP17),
        atol=0.01,
    )
    assert len(a) == len(b) == 500

    # test error
    assert "made_up" not in GAP17.info
    with pytest.raises(KeyError):
        GAP17.random_split([0.5, 0.5], keep_ratio="made_up")


def test_k_fold_split():
    # error messages
    with pytest.raises(ValueError, match="k must be at least 2"):
        GAP17.k_fold_split(k=1)

    # atoms are not hashable, so we set a unique id for each structure
    for i, structure in enumerate(GAP17):
        structure.info["id"] = i

    a, b = GAP17.k_fold_split(5, fold=0, shuffle=False)
    assert a[0] == GAP17[0]

    a, b = GAP17.k_fold_split(5, fold=0)
    assert len(a) == 3624
    assert len(b) == 906
    assert set(a.info["id"]) & set(b.info["id"]) == set()

    c, d = GAP17.k_fold_split(5, fold=1)
    # ensure that b is completely wihin c
    assert set(b.info["id"]) <= set(c.info["id"])

    # ensure that the folds completely cover the dataset
    all_test = []
    for i in range(5):
        _, test = GAP17.k_fold_split(5, fold=i)
        all_test.extend(test.info["id"])

    assert len(set(all_test)) == len(GAP17)

    # test keep ratio
    a, b = GAP17.k_fold_split(k=5, fold=0, keep_ratio="config_type")
    assert np.isclose(
        _get_proportion("bulk_amo", a), _get_proportion("bulk_amo", GAP17)
    )

    # test error
    assert "made_up" not in GAP17.info
    with pytest.raises(KeyError):
        GAP17.k_fold_split(5, fold=0, keep_ratio="made_up")

    with pytest.raises(ValueError, match="only supported when shuffling"):
        GAP17.k_fold_split(5, fold=0, keep_ratio="config_type", shuffle=False)
