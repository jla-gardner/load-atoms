from pathlib import Path

import pytest
from load_atoms.dataset_info import DatasetInfo
from pydantic import ValidationError


def get_correct_dictionary():
    """
    get a dictionary that passes validation
    """

    # this file is root/tests/shared/test_dataset_info.py
    project_root = Path(__file__).parent.parent
    correct_yaml_file = project_root / "database" / "C-GAP-17" / "C-GAP-17.yaml"

    return DatasetInfo.from_yaml_file(correct_yaml_file).model_dump()


def test_incorrect_name():
    kwargs = get_correct_dictionary()
    kwargs["name"] = dict(_not="a string")

    with pytest.raises(ValidationError):
        DatasetInfo(**kwargs)


def test_incorrect_license():
    kwargs = get_correct_dictionary()
    kwargs["license"] = "Not a real license"

    with pytest.raises(ValidationError):
        DatasetInfo(**kwargs)


def test_incorrect_files():
    kwargs = get_correct_dictionary()

    # files should be a mapping of str to checksum

    # not a mapping
    kwargs["files"] = 1
    with pytest.raises(ValidationError):
        DatasetInfo(**kwargs)

    # not a mapping of str to checksum
    kwargs["files"] = {1: 1}
    with pytest.raises(ValidationError):
        DatasetInfo(**kwargs)

    kwargs["files"] = {"file1": "not a hash"}
    with pytest.raises(ValidationError):
        DatasetInfo(**kwargs)


def test_incorrect_citation():
    kwargs = get_correct_dictionary()

    # citation should be a bibtex string
    kwargs["citation"] = "this is not a bibtex string"
    with pytest.raises(ValidationError):
        DatasetInfo(**kwargs)
