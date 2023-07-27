import warnings
from pathlib import Path
from typing import List, Tuple

from ase import Atoms
from ase.io import read

from load_atoms.shared import BASE_REMOTE_URL, UnknownDatasetException
from load_atoms.shared.checksums import matches_checksum
from load_atoms.shared.dataset_info import DatasetId, DatasetInfo

from . import internet


def get_structures_for(
    dataset_id: DatasetId, root: Path
) -> Tuple[List[Atoms], DatasetInfo]:
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


class DataStorage:
    """
    A Class that handles the storage of datasets at a specific path.


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
                description_file_location = BASE_REMOTE_URL + dataset_id + ".yaml"
                internet.download(description_file_location, info_file)
            except Exception as e:
                raise UnknownDatasetException(dataset_id) from e

        info = DatasetInfo.from_file(info_file)

        # download any missing dataset files
        missing_files = {
            file: hash
            for file, hash in info.files.items()
            if not (folder / file).exists()
        }
        remote_files = [info.url_root + file for file in missing_files]
        internet.download_all(remote_files, folder)

        # validate the just-downloaded files
        for file_name, hash in missing_files.items():
            file = folder / file_name
            if not matches_checksum(file, hash):
                warnings.warn(
                    f"Checksum of {file_name} does not match the expected value. "
                    "This means that the downloaded dataset may be corrupted."
                )

    def load_dataset(self, dataset_id) -> Tuple[List[Atoms], DatasetInfo]:
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

        info = DatasetInfo.from_file(info_file)
        structures = []
        for file_name in info.files:
            file = folder / file_name
            structures.extend(read(file, index=":"))

        return structures, info
