import pytest
import requests
from aiohttp import ClientConnectorError

from load_atoms.backend import RequestError, download_structures, download_thing
from load_atoms.util import DATASETS_DIR


@pytest.mark.asyncio
async def test_real_download(tmp_path):
    url = "https://raw.githubusercontent.com/jla-gardner/load-atoms/main/README.md"

    # download the file
    path = tmp_path / "test.json"
    await download_thing(url, path)

    # check that the file exists
    assert path.exists(), "The file was not downloaded"


@pytest.mark.asyncio
async def test_missing_download(tmp_path):
    # attempt to download a file from a non-existent url
    fake_url = "https://this.is.a.fake.url/file.json"
    with pytest.raises(ClientConnectorError):
        await download_thing(fake_url, tmp_path / "test.json")

    # attempt to download a file that does not exist
    # and check that we report on the 404 error
    real_url_fake_file = "https://raw.githubusercontent.com/jla-gardner/load-atoms/main/made_up_file.json"
    with pytest.raises(RequestError, match="404"):
        await download_thing(real_url_fake_file, tmp_path / "test.json")


@pytest.mark.asyncio
async def test_download_structures(tmp_path):
    # test that download structures raises an error if an existing
    # file is corrupted

    fake_url = "https://this.is.a.fake.url/file.extxyz"
    fake_file = tmp_path / "file.extxyz"
    fake_file.write_text("fake file")
    incorrect_hash = "0" * 12

    with pytest.raises(ClientConnectorError):
        await download_structures(fake_url, fake_file, incorrect_hash)

    existing = DATASETS_DIR / "QM7.extxyz"
    new = tmp_path / "QM7.extxyz"
    new.write_bytes(existing.read_bytes())
