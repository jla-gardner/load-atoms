import shutil
from contextlib import nullcontext
from pathlib import Path

import numpy as np
import pytest
from ase import Atoms
from ase.io import read, write
from load_atoms import load_dataset
from load_atoms.atoms_dataset import (
    AtomsDataset,
    LmdbAtomsDataset,
    summarise_dataset,
)
from load_atoms.utils import UnknownDatasetException
from setup import TESTING_DIR

STRUCTURES = [Atoms("H2O"), Atoms("H2O2")]
GAP17 = load_dataset("C-GAP-17", root=TESTING_DIR)

shutil.rmtree(TESTING_DIR / "gap17.lmdb", ignore_errors=True)
LmdbAtomsDataset.save(
    path=TESTING_DIR / "gap17.lmdb",
    structures=GAP17,
    description=GAP17.description,
)
GAP17_LMDB = LmdbAtomsDataset(TESTING_DIR / "gap17.lmdb")


def _is_water_dataset(dataset):
    assert len(dataset) == 2
    assert set(dataset[0].symbols) == {"H", "O"}


def test_dataset_from_structures():
    dataset = load_dataset(STRUCTURES)
    _is_water_dataset(dataset)


def test_dataset_writeable_and_readable(tmp_path):
    dataset = load_dataset(STRUCTURES)
    write(tmp_path / "test.xyz", dataset)

    structures = read(tmp_path / "test.xyz", index=":")
    assert isinstance(structures, list)
    dataset2 = load_dataset(structures)
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


@pytest.mark.parametrize(
    "dataset", [GAP17, GAP17_LMDB], ids=["gap17", "gap17_lmdb"]
)
def test_can_load_from_id(tmp_path, dataset):
    assert len(dataset) == 4530

    with pytest.raises(UnknownDatasetException):
        load_dataset("made_up_dataset", root=tmp_path)


@pytest.mark.parametrize(
    "dataset", [GAP17, GAP17_LMDB], ids=["gap17", "gap17_lmdb"]
)
def test_summarise(dataset):
    summary = summarise_dataset(STRUCTURES)
    assert summary.startswith(
        "Dataset"
    ), "Unknown datasets should start like this"

    summary = repr(dataset)
    assert "energy" in summary, "The summary should contain the property names"
    assert summary.startswith(
        "C-GAP-17"
    ), "The summary should contain the dataset name"


def test_appears_equal():
    assert str(GAP17) == str(GAP17_LMDB)


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
    write(tmp_path / "test.xyz", structure)

    with pytest.warns(
        UserWarning,
        match="single structure",
    ):
        load_dataset(tmp_path / "test.xyz")


@pytest.mark.parametrize(
    "dataset", [GAP17, GAP17_LMDB], ids=["gap17", "gap17_lmdb"]
)
def test_info_and_arrays(dataset):
    context = nullcontext() if dataset is GAP17 else pytest.warns(UserWarning)
    with context:
        assert "energy" in dataset.info
        assert isinstance(dataset.info["energy"], np.ndarray)

    with context:
        assert "positions" in dataset.arrays
        assert dataset.arrays["positions"].shape[-1] == 3


def test_properties():
    dataset = load_dataset(STRUCTURES)

    assert len(dataset) == 2
    assert dataset.n_atoms == 7
    assert (dataset.structure_sizes == [3, 4]).all()


def _get_proportion(config_type, dataset):
    return np.sum(dataset.info["config_type"] == config_type) / len(dataset)


@pytest.mark.parametrize(
    "dataset", [GAP17, GAP17_LMDB], ids=["gap17", "gap17_lmdb"]
)
def test_random_split(dataset):
    # request integer splits
    train, test = dataset.random_split([100, 50])
    assert len(train) == 100
    assert len(test) == 50

    # request float splits
    n = len(dataset)
    a, b, c = dataset.random_split([0.5, 0.25, 0.25])
    assert len(a) == n // 2
    assert len(b) in [n // 4, n // 4 + 1]
    assert len(c) in [n // 4, n // 4 + 1]

    # test keep ratio
    context = nullcontext() if dataset is GAP17 else pytest.warns(UserWarning)
    with context:
        assert "config_type" in dataset.info
        assert "bulk_amo" in dataset.info["config_type"]

        # ... with floats
        a, b = dataset.random_split([0.5, 0.5], keep_ratio="config_type")
        assert len(a) + len(b) == len(dataset)
        assert np.isclose(
            _get_proportion("bulk_amo", a), _get_proportion("bulk_amo", dataset)
        )

        # ... with ints
        a, b = dataset.random_split([500, 500], keep_ratio="config_type")
        assert np.isclose(
            _get_proportion("bulk_amo", a),
            _get_proportion("bulk_amo", dataset),
            atol=0.01,
        )
        assert len(a) == len(b) == 500

    # test error
    assert "made_up" not in dataset.info
    with pytest.raises(KeyError):
        dataset.random_split([0.5, 0.5], keep_ratio="made_up")


@pytest.mark.parametrize(
    "dataset", [GAP17, GAP17_LMDB], ids=["gap17", "gap17_lmdb"]
)
def test_k_fold_split(dataset):
    # error messages
    with pytest.raises(ValueError, match="k must be at least 2"):
        dataset.k_fold_split(k=1)

    # atoms are not hashable, so we set a unique id for each structure
    def get_id(structure):
        return float(
            structure.info["energy"] + np.abs(structure.arrays["forces"]).sum()
        )

    a, b = dataset.k_fold_split(5, fold=0, shuffle=False)
    assert a[0] == dataset[0]

    a, b = dataset.k_fold_split(5, fold=0)
    assert len(a) == 3624
    assert len(b) == 906
    a_ids = set(map(get_id, a))
    b_ids = set(map(get_id, b))
    assert a_ids & b_ids == set()

    c, d = dataset.k_fold_split(5, fold=1)
    c_ids = set(map(get_id, c))
    # ensure that b is completely within c
    assert b_ids <= c_ids

    # ensure that the folds completely cover the dataset
    all_test_ids = []
    for i in range(5):
        _, test = dataset.k_fold_split(5, fold=i)
        all_test_ids.extend(list(map(get_id, test)))

    assert len(set(all_test_ids)) == len(dataset)

    # test keep ratio
    a, b = dataset.k_fold_split(k=5, fold=0, keep_ratio="config_type")
    context = nullcontext() if dataset is GAP17 else pytest.warns(UserWarning)
    with context:
        assert np.isclose(
            _get_proportion("bulk_amo", a), _get_proportion("bulk_amo", dataset)
        )

    # test error
    assert "made_up" not in dataset.info
    with pytest.raises(KeyError):
        dataset.k_fold_split(5, fold=0, keep_ratio="made_up")

    with pytest.raises(ValueError, match="only supported when shuffling"):
        dataset.k_fold_split(5, fold=0, keep_ratio="config_type", shuffle=False)


def test_read_only():
    dataset = GAP17_LMDB
    atoms = dataset[0]
    with pytest.raises(ValueError, match="info"):
        atoms.info["test"] = 1
    with pytest.raises(ValueError, match="arrays"):
        atoms.arrays["test"] = np.zeros((1, 3))


@pytest.mark.parametrize(
    "dataset", [GAP17, GAP17_LMDB], ids=["gap17", "gap17_lmdb"]
)
def test_filtering(dataset: AtomsDataset):
    assert len(dataset) == 4530

    # filter out all but the first 10 structures
    filtered = dataset.filter_by(config_type="bulk_amo")
    assert len(filtered) == 3410

    bool_idx = [
        structure.info["config_type"] == "bulk_amo" for structure in dataset
    ]
    indexed = dataset[bool_idx]
    assert len(indexed) == 3410
    context = nullcontext() if dataset is GAP17 else pytest.warns(UserWarning)
    with context:
        assert np.all(indexed.info["energy"] == filtered.info["energy"])
