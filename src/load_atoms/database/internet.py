from __future__ import annotations

import warnings
from dataclasses import dataclass
from pathlib import Path

import requests

from load_atoms.progress import Progress
from load_atoms.utils import matches_checksum


@dataclass
class FileDownload:
    url: str
    expected_hash: str
    local_name: str = None  # type: ignore

    def __post_init__(self):
        if self.local_name is None:
            self.local_name = Path(self.url).name


def download(url: str, local_path: Path, progress: Progress):
    """
    Download a file from the given url to the given path.

    If path is a file, the file will be downloaded to that path.
    Else, the file will be downloaded to the given path, with the same name as
    the file at the given url.

    Parameters
    ----------
    url
        The url to download the file from.
    local_path
        The path to download the file to.
    progress
        The progress bar to add the download to.
    """

    if local_path.is_dir():
        local_path = local_path / Path(url).name
    local_path.parent.mkdir(parents=True, exist_ok=True)

    with requests.get(url, stream=True) as response, progress.new_task(
        f"Downloading {local_path.name}"
    ) as task, open(local_path, "wb") as f:
        response.raise_for_status()
        file_size = int(response.headers["content-length"])
        task.update(total=file_size)
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
                task.update(advance=len(chunk))


def download_all(
    files: list[FileDownload],
    download_dir: Path,
    progress: Progress,
):
    """
    Download all files and verify their checksums.

    Parameters
    ----------
    files
        A list of FileDownloads
    tmp_dir
        The directory where the files should be saved.
    progress
        A Progress object to track the download progress.
    """

    # 1. download any missing files
    for file in files:
        local_path = download_dir / file.local_name
        if not local_path.exists():
            download(file.url, local_path, progress)

    # 2. verify the hashes of all files
    for file in files:
        local_path = download_dir / file.local_name
        if not matches_checksum(local_path, file.expected_hash):
            warnings.warn(
                f"Checksum mismatch for file: {local_path}",
                stacklevel=2,
            )
