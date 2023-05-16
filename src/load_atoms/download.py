import asyncio
from dataclasses import dataclass
from pathlib import Path
from typing import List

import aiohttp
import nest_asyncio
from rich.progress import Progress


@dataclass
class Download:
    url: str
    save_to: Path


class RequestError(Exception):
    def __init__(self, url: str, code: int):
        message = f"Could not find {url}. Response code: {code}"
        super().__init__(message)


# support for nested asyncio loops, such that we can download
# structures inside a jupyter notebook in parallel
nest_asyncio.apply()


def get_event_loop():
    """
    get the current event loop, or create a new one if none exists

    this is useful for running this code inside a jupyter notebook,
    where an event loop already exists
    """
    loop = asyncio.get_event_loop()
    if loop.is_running():
        loop = asyncio.get_running_loop()
    else:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop


def download_all(tasks: List[Download]):
    """
    download a list of files in parallel
    """

    # use the asyncio event loop to download the files asynchronously
    # and in parrallel
    loop = get_event_loop()
    loop.run_until_complete(_download_all(tasks))


async def _download_all(tasks: List[Download], num_workers: int = 16):
    """
    Download a list of files with up to
    `num_workers` parallel downloads.

    Makes use of a asycnio.Queue to limit the number of parallel downloads,
    and a Rich Progress bar to show the progress.
    """

    # fill our queue with the tasks
    queue = asyncio.Queue()
    for task in tasks:
        queue.put_nowait(task)

    # make some workers to download the files
    async def worker(progress_bar: Progress, callback=None):
        """
        a worker that continuously downloads files from the queue
        and updates the progress bar
        """
        while True:
            # this loop runs forever, until this worker is cancelled
            task = await queue.get()
            await download_file(task.url, task.save_to, progress_bar)
            if callback is not None:
                callback()
            queue.task_done()

    # create a progress bar
    with Progress(transient=True) as progress:
        # overall progress bar
        task = progress.add_task(f"Downloading files", total=len(tasks))
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


async def download_file(
    url: str, save_to: Path, progress: Progress = None, task_description: str = None
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
            if response.status != 200:
                raise RequestError(url, response.status)

            total_length = int(response.headers.get("content-length", 0))
            if progress is not None:
                task = progress.add_task(task_description, total=total_length)

            with save_to.open("wb") as f:
                async for chunk in response.content.iter_chunked(1024):
                    f.write(chunk)
                    if progress is not None:
                        progress.update(task, advance=len(chunk))

            if progress is not None:
                progress.remove_task(task)
