import os

from load_atoms import load_dataset
from setup import TESTING_DIR


def test_verbose(capfd):
    # Test verbose output
    os.environ["LOAD_ATOMS_VERBOSE"] = "1"
    captured = capfd.readouterr()
    load_dataset("C-GAP-17", root=TESTING_DIR)
    captured = capfd.readouterr()
    assert "C-GAP-17" in captured.out

    # Test non-verbose output
    os.environ["LOAD_ATOMS_VERBOSE"] = "0"
    load_dataset("C-GAP-17", root=TESTING_DIR)
    captured = capfd.readouterr()
    assert "C-GAP-17" not in captured.out
