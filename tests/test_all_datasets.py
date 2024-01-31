"""
test all the datasets in the load-atoms database
"""

import shutil
from pathlib import Path

import pytest
from load_atoms import dataset
from load_atoms.dataset import DescribedDataset
from load_atoms.utils import matches_checksum

# this file is at root/tests/database/test_all_datasets.py
project_root = Path(__file__).parent.parent

# database is at root/database
databaset_root = project_root / "database"
dataset_names = sorted([p.name for p in databaset_root.iterdir() if p.is_dir()])


# copy over the datasets to a place to test them
testing_dir = project_root / "testing-datasets"
testing_dir.mkdir(exist_ok=True)

for name in dataset_names:
    # copy over the folder if it doesn't exist
    if not (testing_dir / name).exists():
        shutil.copytree(databaset_root / name, testing_dir / name)


@pytest.mark.parametrize("name", dataset_names, ids=dataset_names)
def test_dataset(name):
    """Test that the dataset can be loaded."""

    # ignore the really big datasets to save on time
    to_ignore = ["C-SYNTH-23M"]
    if name in to_ignore:
        pytest.skip(f"Skipping {name}")

    ds: DescribedDataset = dataset(name, root=testing_dir)  # type: ignore

    # check that all files match their checksums
    for filename, hash in ds.description.files.items():
        file = testing_dir / name / filename
        assert matches_checksum(file, hash)


@pytest.mark.parametrize("name", dataset_names, ids=dataset_names)
def test_docs_exist(name):
    """Test that documentation exists for each dataset."""

    docs = project_root / "docs/source/datasets"

    assert (docs / f"{name}.rst").exists(), f"Missing docs for {name}"
