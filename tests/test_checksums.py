from load_atoms.utils import generate_checksum, matches_checksum


def test_matches_contents(tmp_path):
    """
    Test that check_file_contents returns True if the contents of a file
    match the given hash.
    """

    fake_file = tmp_path / "file.txt"
    fake_file.write_text("fake file")

    correct_hash = generate_checksum(fake_file)
    incorrect_hash = "0" * 12

    assert matches_checksum(fake_file, correct_hash)
    assert not matches_checksum(fake_file, incorrect_hash)
    assert not matches_checksum(fake_file, correct_hash[:-1])
