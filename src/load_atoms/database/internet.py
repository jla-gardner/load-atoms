from __future__ import annotations

from pathlib import Path

import requests

from load_atoms.progress import Progress


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

    with requests.get(url, stream=True) as response, progress.new_task(
        f"Downloading {Path(url).name}"
    ) as task, open(local_path, "wb") as f:
        response.raise_for_status()
        file_size = int(response.headers["content-length"])
        task.update(total=file_size)
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
                task.update(advance=len(chunk))
