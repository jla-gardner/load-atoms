import pytest
from load_atoms import load_dataset
from load_atoms.database import DatabaseEntry
from setup import (
    AVAILABLE_DATASETS,
    DATABASE_ROOT,
    PROJECT_ROOT,
    TESTING_DIR,
)


@pytest.mark.parametrize("name", AVAILABLE_DATASETS, ids=AVAILABLE_DATASETS)
def test_correctness(name):
    # check that the dataset entry is valid for all datasets
    DatabaseEntry.from_yaml_file(DATABASE_ROOT / name / f"{name}.yaml")

    # skip big tests for now
    # TODO: elegant way to enable these sometimes?
    if name in [
        "AC-2D-22",
        "QM9",
        "C-SYNTH-23M",
        "SiO2-GAP-22",
        "ANI-1ccx",
        "ANI-1x",
        "rMD17",
    ]:
        return

    # naive test that the dataset loads without error
    load_dataset(name, root=TESTING_DIR)


@pytest.mark.parametrize("name", AVAILABLE_DATASETS, ids=AVAILABLE_DATASETS)
def test_docs_exist(name):
    docs = PROJECT_ROOT / "docs/source/datasets"

    assert (docs / f"{name}.rst").exists(), f"Missing docs for {name}"
