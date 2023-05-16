import pytest
from aiohttp import ClientConnectorError

from load_atoms.download import Download, RequestError, download_all, download_file


@pytest.mark.asyncio
async def test_download_real_file(tmp_path):
    url = "https://raw.githubusercontent.com/jla-gardner/load-atoms/main/README.md"

    # download the file
    path = tmp_path / "test.md"
    await download_file(url, path)

    # check that the file exists
    assert path.exists(), "The file was not downloaded"
    assert "load-atoms" in path.read_text(), "The file contents are incorrect"


@pytest.mark.asyncio
async def test_download_fake_file(tmp_path):
    # attempt to download a file from a non-existent url
    fake_url = "https://this.is.a.fake.url/file.json"
    with pytest.raises(ClientConnectorError):
        await download_file(fake_url, tmp_path / "test.json")

    # attempt to download a file tfrom a real server,
    # but hat does not exist
    # and check that we report on the 404 error
    real_url_fake_file = "https://raw.githubusercontent.com/jla-gardner/load-atoms/main/made_up_file.json"
    with pytest.raises(RequestError, match="404"):
        await download_file(real_url_fake_file, tmp_path / "test.json")


def test_download_all(tmp_path):
    base_url = url = "https://raw.githubusercontent.com/jla-gardner/load-atoms/main/"
    tasks = [
        Download(base_url + "README.md", tmp_path / "README.md"),
        Download(base_url + "LICENSE", tmp_path / "LICENSE"),
    ]
    download_all(tasks)

    for task in tasks:
        assert task.save_to.exists(), "The file was not downloaded"
        assert task.save_to.read_text() != "", "The file contents are incorrect"
