import pytest
import yaml

from load_atoms.checksums import generate_checksum
from load_atoms.database import _DESCRIPTOR_FILES, DATASETS, DESCRIPTION_BLUEPRINT
from load_atoms.util import get_dataset_file


@pytest.mark.parametrize("file", _DESCRIPTOR_FILES, ids=lambda x: x.name)
def test_description_file(file):
    """
    test that all dataset description files are valid
    """
    with open(file) as f:
        DESCRIPTION_BLUEPRINT.validate(yaml.safe_load(f))


def test_all_loaded():
    """
    test that all datasets are loaded
    """
    assert len(DATASETS) == len(_DESCRIPTOR_FILES)


@pytest.mark.parametrize("dataset", DATASETS.values(), ids=lambda x: x.name)
def test_checksums(dataset):
    """
    test that all dataset checksums are valid
    """
    for path, checksum in dataset.files.items():
        path = get_dataset_file(path)
        assert checksum == generate_checksum(path)
