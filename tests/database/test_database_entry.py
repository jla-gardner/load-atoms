import pytest
from load_atoms.database import DatabaseEntry
from pydantic import ValidationError

from ..setup import PROJECT_ROOT


def get_correct_dictionary():
    """
    get a dictionary that passes validation
    """

    correct_yaml_file = PROJECT_ROOT / "database" / "C-GAP-17" / "C-GAP-17.yaml"

    return DatabaseEntry.from_yaml_file(correct_yaml_file).model_dump()


def test_incorrect_name():
    kwargs = get_correct_dictionary()
    kwargs["name"] = dict(_not="a string")

    with pytest.raises(ValidationError):
        DatabaseEntry(**kwargs)


def test_incorrect_license():
    kwargs = get_correct_dictionary()
    kwargs["license"] = "Not a real license"

    with pytest.raises(ValidationError):
        DatabaseEntry(**kwargs)


def test_incorrect_citation():
    kwargs = get_correct_dictionary()

    # citation should be a bibtex string
    kwargs["citation"] = "this is not a bibtex string"
    with pytest.raises(ValidationError):
        DatabaseEntry(**kwargs)
