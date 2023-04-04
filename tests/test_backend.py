import pytest
import requests

from load_atoms.backend import download_thing


def test_real_download(tmp_path):
    # this is a test file that is 1kb
    url = "https://file-examples.com/storage/fef89aabc36429826928b9c/2017/02/file_example_JSON_1kb.json"

    # download the file
    path = tmp_path / "test.json"
    download_thing(url, path)

    # check that the file exists
    assert path.exists(), "The file was not downloaded"


def test_missing_download(tmp_path):
    # attempt to download a file from a non-existent url
    fake_url = "https://this.is.a.fake.url/file.json"
    with pytest.raises(requests.exceptions.ConnectionError):
        download_thing(fake_url, tmp_path / "test.json")

    # attempt to download a file that does not exist
    # and check that we report on the 404 error
    real_url_fake_file = "https://raw.githubusercontent.com/jla-gardner/load-atoms/main/made_up_file.json"
    with pytest.raises(ValueError, match="404"):
        download_thing(real_url_fake_file, tmp_path / "test.json")