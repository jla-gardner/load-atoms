import pytest
from load_atoms.database.backend import load_dataset_by_id
from load_atoms.utils import UnknownDatasetException


# @pytest.mark.xfail
def test_load_dataset(tmp_path):
    dataset = load_dataset_by_id("C-GAP-17", tmp_path)
    assert len(dataset) == 4530, "Incorrect number of structures"
    assert dataset.description is not None, "Dataset description is missing"
    assert dataset.description.name == "C-GAP-17", "Incorrect dataset name"

    assert (
        tmp_path / "database-entries" / "C-GAP-17.yaml"
    ).exists(), "Dataset description missing"
    assert (tmp_path / "C-GAP-17.pkl").exists(), "Structures are missing"

    with pytest.raises(UnknownDatasetException):
        load_dataset_by_id("made_up_dataset", tmp_path)
