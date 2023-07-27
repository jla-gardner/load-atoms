from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import List

import requests
from rich.progress import Progress, TaskID


def download(url: str, local_path: Path):
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
    """

    with Progress(transient=True) as progress:
        task = progress.add_task(f"Downloading {Path(url).name}", start=False)
        _download_with_progress(url, local_path, progress, task)


def download_all(urls: List[str], directory: Path):
    """
    Download all files from the given urls to the given directory.

    Parameters
    ----------
    urls
        A list of urls to download the files from.
    directory
        The directory to download the files to.
    """

    if len(urls) == 0:
        return

    if len(urls) == 1:
        download(urls[0], directory)
        return

    pool_exectutor = ThreadPoolExecutor(max_workers=8, thread_name_prefix="download")
    futures = []
    with Progress(transient=True) as progress, pool_exectutor as pool:
        for url in urls:
            task = progress.add_task(f"Downloading {Path(url).name}", start=False)
            future = pool.submit(
                _download_with_progress, url, directory, progress, task
            )
            futures.append((future, url))

    failures = []
    for future, url in futures:
        try:
            future.result()
        except Exception as e:
            failures.append(url)

    if len(failures) > 0:
        raise Exception(f"Failed to download {len(failures)} files: {failures}")

    pool_exectutor.shutdown()


def _download_with_progress(
    url: str, local_path: Path, progress: Progress, task: TaskID
):
    """
    download the file at the given url to the given path, and update the given
    progress bar as the file is downloaded.
    """
    if local_path.is_dir():
        local_path = local_path / Path(url).name
    local_path.parent.mkdir(parents=True, exist_ok=True)

    with requests.get(url, stream=True) as response:
        # raise an exception if the request was not successful
        response.raise_for_status()

        file_size = int(response.headers.get("content-length", 0))
        progress.update(task, total=file_size)
        progress.start_task(task)

        with open(local_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
                    progress.update(task, advance=len(chunk))
