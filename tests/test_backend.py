import pytest

from load_atoms.backend import CorruptionError, check_file_contents
from load_atoms.checksums import generate_checksum


def test_check_file_contents(tmp_path):
    # test that check_file_contents raises an error if an existing
    # file is corrupted

    fake_file = tmp_path / "file.extxyz"
    fake_file.write_text("fake file")

    correct_hash = generate_checksum(fake_file)
    incorrect_hash = "0" * 12

    assert check_file_contents(fake_file, correct_hash)

    with pytest.raises(CorruptionError):
        check_file_contents(fake_file, incorrect_hash)
