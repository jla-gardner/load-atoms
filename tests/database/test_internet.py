import pytest
from load_atoms.database.internet import download
from load_atoms.progress import SilentProgress

RAW_GITHUB_URL = (
    "https://raw.githubusercontent.com/jla-gardner/load-atoms/main/"
)

_dummy_progress_bar = SilentProgress("dummy")


def test_download(tmp_path):
    url = RAW_GITHUB_URL + "README.md"
    save_to = tmp_path / "test"

    # check downloading to explicit file works:
    download(url, save_to, _dummy_progress_bar)
    assert save_to.exists()

    # check downloading to directory works:
    download(url, tmp_path, _dummy_progress_bar)
    assert (tmp_path / "README.md").exists()

    fake_url = RAW_GITHUB_URL + "fake-file.txt"
    with pytest.raises(Exception):
        download(fake_url, save_to, _dummy_progress_bar)
