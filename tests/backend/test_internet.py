from load_atoms.backend.internet import download


def test_download(tmp_path):
    url = "https://raw.githubusercontent.com/jla-gardner/load-atoms/main/README.md"
    save_to = tmp_path / "test"

    # check downloading to explicit file works:
    download(url, save_to)
    assert save_to.exists()

    # check downloading to directory works:
    download(url, tmp_path)
    assert (tmp_path / "README.md").exists()
