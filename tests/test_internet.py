import pytest
from load_atoms.backend import download, download_all

RAW_GITHUB_URL = (
    "https://raw.githubusercontent.com/jla-gardner/load-atoms/main/"
)


def test_download(tmp_path):
    url = RAW_GITHUB_URL + "README.md"
    save_to = tmp_path / "test"

    # check downloading to explicit file works:
    download(url, save_to)
    assert save_to.exists()

    # check downloading to directory works:
    download(url, tmp_path)
    assert (tmp_path / "README.md").exists()

    fake_url = RAW_GITHUB_URL + "fake-file.txt"
    with pytest.raises(Exception):
        download(fake_url, save_to)


def test_download_all(tmp_path):
    # download_all on nothing should do nothing
    download_all([], tmp_path)

    # download a few files we know exist
    files = ["README.md", "LICENSE", ".gitignore"]
    urls = [RAW_GITHUB_URL + f for f in files]
    download_all(urls, tmp_path)
    assert all((tmp_path / f).exists() for f in files)

    # attempt to download a file that doesn't exist
    with pytest.raises(Exception):
        download_all([RAW_GITHUB_URL + "fake-file.txt", *urls], tmp_path)
