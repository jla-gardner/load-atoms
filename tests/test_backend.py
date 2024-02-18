import pytest
from load_atoms.database.backend import load_structures
from load_atoms.utils import UnknownDatasetException


def test_get_structures_for(tmp_path):
    """
    Test that load_structures returns the correct structures
    """

    structures, info = load_structures("C-GAP-17", tmp_path)

    assert len(structures) == 4530, "Incorrect number of structures"
    assert info.name == "C-GAP-17", "Incorrect dataset name"

    folder = tmp_path / "C-GAP-17"
    assert (folder / "C-GAP-17.yaml").exists(), "Dataset description missing"
    assert (folder / "temp" / "C-GAP-17.extxyz").exists(), "Download is missing"
    assert (folder / "C-GAP-17.xyz").exists(), "Structures are missing"

    with pytest.raises(UnknownDatasetException):
        load_structures("made_up_dataset", tmp_path)
