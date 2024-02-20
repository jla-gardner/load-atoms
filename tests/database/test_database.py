import pytest
from load_atoms import load_dataset
from load_atoms.database import DatabaseEntry
from load_atoms.utils import matches_checksum
from setup import (
    AVAILABLE_DATASETS,
    DATABASE_ROOT,
    PROJECT_ROOT,
    TESTING_DIR,
)


@pytest.mark.parametrize("name", AVAILABLE_DATASETS, ids=AVAILABLE_DATASETS)
def test_correctness(name):
    # check that the dataset entry is valid for all datasets
    info = DatabaseEntry.from_yaml_file(DATABASE_ROOT / name / f"{name}.yaml")

    # if the files are hosted on a remote server, finish the test here
    if info.url_root is not None:
        return

    load_dataset(name, root=TESTING_DIR)

    # check that all files match their checksums
    for filename, hash in info.files.items():
        file = TESTING_DIR / name / "temp" / filename
        assert matches_checksum(file, hash)


@pytest.mark.parametrize("name", AVAILABLE_DATASETS, ids=AVAILABLE_DATASETS)
def test_docs_exist(name):
    docs = PROJECT_ROOT / "docs/source/datasets"

    assert (docs / f"{name}.rst").exists(), f"Missing docs for {name}"
