"""
test all the datasets in the load-atoms database
"""

import shutil
from pathlib import Path

import pytest

from load_atoms import dataset
from load_atoms.shared.checksums import matches_checksum

# this file is at root/tests/database/test_all_datasets.py
project_root = Path(__file__).parent.parent.parent

# database is at root/database
databaset_root = project_root / "database"
dataset_names = sorted([p.name for p in databaset_root.iterdir() if p.is_dir()])

# ignore the really big datasets to save on time
to_ignore = ["C-SYNTH-23M"]
dataset_names = [name for name in dataset_names if name not in to_ignore]

# copy over the datasets to a place to test them
testing_dir = project_root / "testing-datasets"
testing_dir.mkdir(exist_ok=True)

for name in dataset_names:
    # copy over the folder if it doesn't exist
    if not (testing_dir / name).exists():
        shutil.copytree(databaset_root / name, testing_dir / name)


@pytest.mark.parametrize("name", dataset_names)
def test_dataset(name):
    """Test that the dataset can be loaded."""

    ds = dataset(name, root=testing_dir)

    # check that all files match their checksums
    for filename, hash in ds._description.files.items():  # type: ignore
        file = testing_dir / name / filename
        assert matches_checksum(file, hash)
