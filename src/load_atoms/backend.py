from __future__ import annotations

import warnings
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import requests
from ase import Atoms
from ase.io import read
from rich.progress import Progress, TaskID, track

from load_atoms.dataset_info import DatasetId, DatasetInfo
from load_atoms.utils import UnknownDatasetException, matches_checksum


def get_structures_for(
    dataset_id: DatasetId, root: Path
) -> tuple[list[Atoms], DatasetInfo]:
    """
    Get the structures comprising the dataset with the given id, either by
    downloading them from the web or by loading them from disk at the given
    path.

    Parameters
    ----------
    dataset_id
        The id of the dataset to load.
    path
        The path to save the structures to.

    Returns
    -------
    List[Atoms]
        The structures comprising the dataset.
    """

    storage = DataStorage(root)
    # if the dataset doesn't already exist, download it from the web,
    # validate it and save it to the given path
    storage.download_missing(dataset_id)

    return storage.load_dataset(dataset_id)


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


def download_all(urls: list[str], directory: Path):
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

    pool_exectutor = ThreadPoolExecutor(
        max_workers=8, thread_name_prefix="download"
    )
    futures = []
    with Progress(transient=True) as progress, pool_exectutor as pool:
        for url in urls:
            task = progress.add_task(
                f"Downloading {Path(url).name}", start=False
            )
            future = pool.submit(
                _download_with_progress, url, directory, progress, task
            )
            futures.append((future, url))

    failures = []
    for future, url in futures:
        try:
            future.result()
        except Exception:
            failures.append(url)

    if len(failures) > 0:
        raise Exception(f"Failed to download {len(failures)} files: {failures}")

    pool_exectutor.shutdown()


class DataStorage:
    """
    Handle the storage of datasets at a specific path.

    Each dataset is stored in a sub-directory with name <dataset_id>.
    Within this directory, the dataset description is stored in a .yaml
    file, together with the structure files.

    Parameters
    ----------
    home
        The path to store the datasets at.
    """

    def __init__(self, root: Path):
        self.root = root

    def _sub_folder_for(self, dataset_id):
        return self.root / dataset_id

    def download_missing(self, dataset_id: DatasetId):
        """
        Download the dataset with the given id from the web and validate it.

        Parameters
        ----------
        dataset_id
            The id of the dataset to download.
        """

        folder = self._sub_folder_for(dataset_id)
        folder.mkdir(parents=True, exist_ok=True)
        info_file = folder / (dataset_id + ".yaml")

        if not info_file.exists():
            # download the dataset description file
            try:
                download(
                    DatasetInfo.description_file_url(dataset_id),
                    info_file,
                )
            except Exception as e:
                raise UnknownDatasetException(dataset_id) from e

        info = DatasetInfo.from_yaml_file(info_file)

        # download any missing dataset files
        missing_files = {
            file: hash
            for file, hash in info.files.items()
            if not (folder / file).exists()
        }

        remote_file_locations = [
            url
            for url in info.remote_file_locations()
            if Path(url).name in missing_files
        ]

        download_all(remote_file_locations, folder)

        # validate the just-downloaded files
        for file_name, hash in missing_files.items():
            file = folder / file_name
            if not matches_checksum(file, hash):
                warnings.warn(
                    f"Checksum of {file_name} does not match the "
                    "expected value. This means that the downloaded dataset "
                    "may be corrupted.",
                    stacklevel=2,
                )

    def load_dataset(self, dataset_id) -> tuple[list[Atoms], DatasetInfo]:
        """
        Load the dataset with the given id from the given path.

        Parameters
        ----------
        dataset_id
            The id of the dataset to load.

        Returns
        -------
        List[Atoms]
            The structures comprising the dataset.
        """

        folder = self._sub_folder_for(dataset_id)
        info_file = folder / (dataset_id + ".yaml")

        info = DatasetInfo.from_yaml_file(info_file)
        structures = []

        iterator = info.files
        if len(info.files) > 3:
            # show a progress bar if there are many files
            iterator = track(
                info.files,
                description=f"Reading files from disk for {dataset_id}",
                transient=True,
            )

        for file_name in iterator:
            file = folder / file_name
            structures.extend(read(file, index=":"))

        return structures, info
