"""
test all the datasets in the load-atoms database
"""

import shutil
from pathlib import Path

import pytest
from load_atoms import load_dataset
from load_atoms.database import DatabaseEntry
from load_atoms.utils import matches_checksum

# this file is at root/tests/database/test_all_datasets.py
project_root = Path(__file__).parent.parent

# database is at root/database
databaset_root = project_root / "database"
dataset_names = sorted([p.name for p in databaset_root.iterdir() if p.is_dir()])

# SIMULATE DOWNLOADING THE DATASETS
# copy over the datasets to a place to test them
testing_dir = project_root / "testing-datasets"
testing_dir.mkdir(exist_ok=True)

for name in dataset_names:
    # copy over the folder if it doesn't exist
    shutil.copytree(
        databaset_root / name, testing_dir / name, dirs_exist_ok=True
    )
    (testing_dir / name / "temp").mkdir(exist_ok=True)
    # move all non yaml files to temp to simulate a download
    for file in (testing_dir / name).glob("*"):
        if (
            file.suffix != ".yaml"
            and file.name != "temp"
            and file.name != f"{name}.xyz"
        ):
            file.rename(testing_dir / name / "temp" / file.name)


@pytest.mark.parametrize("name", dataset_names, ids=dataset_names)
def test_dataset(name):
    """Test that the dataset can be loaded."""

    # check that the dataset entry is valid for all datasets
    info = DatabaseEntry.from_yaml_file(databaset_root / name / f"{name}.yaml")

    # if the files are hosted on a remote server, finish the test here
    if info.url_root is not None:
        return

    load_dataset(name, root=testing_dir)

    # check that all files match their checksums
    for filename, hash in info.files.items():
        file = testing_dir / name / "temp" / filename
        assert matches_checksum(file, hash)


@pytest.mark.parametrize("name", dataset_names, ids=dataset_names)
def test_docs_exist(name):
    """Test that documentation exists for each dataset."""

    docs = project_root / "docs/source/datasets"

    assert (docs / f"{name}.rst").exists(), f"Missing docs for {name}"
