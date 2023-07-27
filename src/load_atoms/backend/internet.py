import asyncio
from collections import namedtuple
from pathlib import Path
from typing import List, Optional

import aiohttp
import nest_asyncio
import requests
from rich.progress import Progress, track

from load_atoms.util import do_nothing


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
    if local_path.is_dir():
        local_path = local_path / Path(url).name

    with requests.get(url, stream=True) as response:
        # raise an exception if the request was not successful
        response.raise_for_status()

        with open(local_path, "wb") as f:
            file_size = int(response.headers.get("content-length", 0))
            large_file = file_size > 10 * 1024 * 1024  # 10 MB threshold

            chunk_stream = response.iter_content(chunk_size=1024)
            if large_file:
                chunk_stream = track(
                    chunk_stream,
                    total=file_size,
                    description=f"Downloading {local_path.name}...",
                )

            for chunk in chunk_stream:
                if chunk:
                    f.write(chunk)


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

    if len(urls) <= 3:
        for url in urls:
            download(url, directory)
        return

    # async download all files if there are more than three
    run_until_complete(_async_download_all(urls, directory))


def run_until_complete(future):
    # support for nested asyncio loops, such that we can run
    # asyncio code from within a Jupyter notebook
    nest_asyncio.apply()

    loop = asyncio.get_event_loop()
    if loop.is_running():
        loop = asyncio.get_running_loop()
    else:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    loop.run_until_complete(future)


async def _async_download_all(
    urls: List[str],
    directory: Path,
    num_workers: int = 16,
):
    """
    Download a list of files with up to
    `num_workers` parallel downloads.

    Makes use of a asycnio.Queue to limit the number of parallel downloads,
    and a Rich Progress bar to show the progress.
    """
    Task = namedtuple("Task", ["url", "save_to"])

    # build our queue of tasks
    queue = asyncio.Queue()
    for url in urls:
        queue.put_nowait(Task(url, directory / Path(url).name))

    # make some workers to download the files
    async def worker(progress_bar: Progress, callback=None):
        """
        a worker that continuously downloads files from the queue
        and updates the progress bar
        """
        while True:
            # this loop runs until this worker is cancelled
            task = await queue.get()
            await _async_download(task.url, task.save_to, progress_bar)
            if callback is not None:
                callback()
            queue.task_done()

    # create a progress bar
    with Progress(transient=True) as progress:
        # overall progress bar
        task = progress.add_task(f"Downloading files", total=len(urls))
        update_total = lambda: progress.update(task, advance=1)

        # create some workers: this automatically starts them
        workers = [
            asyncio.create_task(worker(progress, callback=update_total))
            for _ in range(num_workers)
        ]

        # wait for the queue to be empty, i.e. all files have been downloaded
        await queue.join()

        # wait until all workers are cancelled
        for worker in workers:
            worker.cancel()
        await asyncio.gather(*workers, return_exceptions=True)

        # everything is now downloaded!


async def _async_download(
    url: str,
    save_to: Path,
    progress: Optional[Progress] = None,
    task_description: Optional[str] = None,
):
    """
    Download a file from the internet.

    Optionally use a Rich Progress bar to show the progress.
    """

    if task_description is None:
        task_description = save_to.name

    save_to.parent.mkdir(parents=True, exist_ok=True)

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            # raise an exception if the request was not successful
            response.raise_for_status()

            total_length = int(response.headers.get("content-length", 0))

            if progress is not None:
                task = progress.add_task(task_description, total=total_length)
                callback = lambda chunk: progress.update(task, advance=len(chunk))
                cleanup = lambda: progress.remove_task(task)
            else:
                callback = do_nothing
                cleanup = do_nothing

            with save_to.open("wb") as f:
                async for chunk in response.content.iter_chunked(1024):
                    f.write(chunk)
                    callback(chunk)

            cleanup()
