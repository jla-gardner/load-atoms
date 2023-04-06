from pathlib import Path

import pytest
from pydantic import ValidationError

from load_atoms.checksums import generate_checksum
from load_atoms.database import (
    DATASETS,
    DatasetDescription,
    find_all_descriptor_files,
    get_description_of,
)

_local_path_to_datasets = Path(__file__).parent.parent / "src/load_atoms/datasets"


def test_all_loaded():
    """
    test that all datasets are loaded
    """

    assert len(DATASETS) == len(find_all_descriptor_files())


@pytest.mark.parametrize("dataset", DATASETS.values(), ids=lambda x: x.name)
def test_checksums(dataset):
    """
    test that all dataset checksums are correct
    """

    for path, checksum in dataset.files.items():
        path = _local_path_to_datasets / path
        assert checksum == generate_checksum(path)


def test_description():
    desc = get_description_of("C-GAP-17")
    assert desc.name == "C-GAP-17"


def get_correct_dict():
    return DATASETS["C-GAP-17"].dict()


def test_incorrect_name():
    kwargs = get_correct_dict()
    kwargs["name"] = dict(_not="a string")

    with pytest.raises(ValidationError):
        DatasetDescription(**kwargs)


def test_incorrect_license():
    kwargs = get_correct_dict()
    kwargs["license"] = "Not a real license"

    with pytest.raises(ValidationError):
        DatasetDescription(**kwargs)


def test_incorrect_files():
    kwargs = get_correct_dict()

    # files should be a mapping of str to checksum

    # not a mapping
    kwargs["files"] = 1
    with pytest.raises(ValidationError):
        DatasetDescription(**kwargs)

    # not a mapping of str to checksum
    kwargs["files"] = {1: 1}
    with pytest.raises(ValidationError):
        DatasetDescription(**kwargs)


def test_incorrect_citation():
    kwargs = get_correct_dict()

    # citation should be a bibtex string
    kwargs["citation"] = "this is not a bibtex string"
    with pytest.raises(ValidationError):
        DatasetDescription(**kwargs)
