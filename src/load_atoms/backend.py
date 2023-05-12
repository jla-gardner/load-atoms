"""
The backend is responsible for downloading the datasets when they 
are first loaded, and for loading these datasets into memory, via
the `get_structures` function. 
"""

import asyncio
from pathlib import Path
from typing import List

import aiohttp
import nest_asyncio
from ase import Atoms
from ase.io import read

from load_atoms.checksums import generate_checksum
from load_atoms.database import DatasetDescription
from load_atoms.util import DEFAULT_DOWNLOAD_DIR

# support for nested asyncio loops, such that we can download
# structures inside a jupyter notebook in parallel
nest_asyncio.apply()


def get_event_loop():
    loop = asyncio.get_event_loop()
    if loop.is_running():
        loop = asyncio.get_running_loop()
    else:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop


class RequestError(Exception):
    def __init__(self, url: str, code: int):
        message = f"Could not find {url}. Response code: {code}"
        super().__init__(message)


class CorruptionError(Exception):
    def __init__(self, path: Path):
        super().__init__(
            f"File {path} exists, but did not match the expected checksum."
            "Please move this file to a different location, or delete it."
        )


def get_structures(dataset: DatasetDescription, root: Path = None) -> List[Atoms]:
    """
    Get the structures associated with a dataset.
    """

    # if no root is specified, use the default download directory
    if root is None:
        root = DEFAULT_DOWNLOAD_DIR
    root = Path(root)

    # first, we download any missing files:
    loop = get_event_loop()
    loop.run_until_complete(download_missing_files(dataset, root))

    # now, we can load the structures from the files
    print(f"Loading {dataset.name} from disk...")
    all_structures = []
    for file, hash in dataset.files.items():
        local_path = root / file
        check_file_contents(local_path, hash)
        structures = read(local_path, index=":")
        all_structures.extend(structures)

    return all_structures


async def download_missing_files(
    dataset: DatasetDescription, root: Path = None
) -> None:
    tasks = []
    for file, hash in dataset.files.items():
        local_path = root / file

        if local_path.exists():
            continue

        remote_url = dataset.url_root + file
        download_task = download_structures(
            remote_url,
            local_path,
            hash,
            f"Downloading {file}",
        )
        tasks.append(download_task)

    if not tasks:
        return

    # wait for all downloads to finish
    print(f"Downloading {len(tasks)} files...")
    await asyncio.wait(tasks)


def check_file_contents(local_path: Path, expected_file_hash: str) -> bool:
    file_hash = generate_checksum(local_path)
    if expected_file_hash != file_hash:
        raise CorruptionError(
            f"The dataset on disk at {local_path} has been corrupted.\n"
            "If you have made changes to this, "
            "please revert them or move/delete the file."
        )
    return True


async def download_structures(
    remote_url: str, local_path: Path, expected_file_hash: str, message: str = None
):
    if message is not None:
        print(message)

    local_path.parent.mkdir(parents=True, exist_ok=True)
    await download_thing(remote_url, local_path)

    if not local_path.exists():
        raise ValueError(
            "There was a problem downloading the dataset.\nPlease try again."
        )


async def download_thing(url: str, save_to: Path) -> None:
    """Download a thing from the internet."""

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status != 200:
                raise RequestError(url, response.status)

            data = await response.read()
            save_to.write_bytes(data)
