import pytest
from load_atoms.backend import get_structures_for
from load_atoms.utils import UnknownDatasetException


def test_get_structures_for(tmp_path):
    """
    Test that get_structures_for returns the correct structures
    """

    structures, info = get_structures_for("C-GAP-17", tmp_path)

    assert len(structures) == 4530, "Incorrect number of structures"
    assert info.name == "C-GAP-17", "Incorrect dataset name"

    folder = tmp_path / "C-GAP-17"
    assert (folder / "C-GAP-17.yaml").exists(), "Dataset description missing"
    assert (folder / "C-GAP-17.extxyz").exists(), "Structure file missing"

    with pytest.raises(UnknownDatasetException):
        get_structures_for("made_up_dataset", tmp_path)
