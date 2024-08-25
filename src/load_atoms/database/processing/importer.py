from __future__ import annotations

import shutil
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Iterator

import ase.io
from ase import Atoms

from load_atoms.atoms_dataset import AtomsDataset
from load_atoms.database.internet import download as _download
from load_atoms.progress import Progress
from load_atoms.utils import matches_checksum

BASE_GITHUB_URL = "https://github.com/jla-gardner/load-atoms/raw/main/database"


def download_file(url: str, file_path: Path, expected_hash: str):
    """
    Download a file from the given URL and verify its checksum.

    Parameters
    ----------
    url : str
        The URL to download the file from.
    file_path : Path
        The path where the file should be saved.
    expected_hash : str
        The expected hash of the downloaded file.

    Raises
    ------
    ValueError
        If the downloaded file's checksum doesn't match the expected hash.
    """
    progress = Progress("Downloading", transient=True)
    _download(url, file_path, progress)

    if not matches_checksum(file_path, expected_hash):
        raise ValueError(f"Checksum mismatch for downloaded file: {file_path}")


class BaseImporter(ABC):
    def __init__(
        self,
        urls: dict[str, str],
        processing_dir: str,
        cleanup: bool = True,
    ):
        """
        Initialize the BaseImporter.

        Parameters
        ----------
        processing_dir
            The relative directory where the dataset is processed.
        urls
            A mapping from urls to expected file hashes.
        cleanup
            Whether to clean up the temporary directory after processing.
        """
        self.urls = urls
        self.processing_dir = processing_dir
        self.cleanup = cleanup

    @abstractmethod
    def process(self, tmp_dir: Path) -> Iterator[Atoms]:
        """
        Iterate over ase.Atoms objects.

        Parameters
        ----------
        tmp_dir
            The temporary directory where downloaded files are stored.

        Yields
        ------
        Atoms
            An iterator of ASE Atoms objects processed from the downloaded files
        """

    def get_dataset(self, root_dir: Path) -> AtomsDataset:
        """
        Get the dataset for this importer.
        """
        # create a temporary directory for the dataset
        tmp_dir = root_dir / self.processing_dir
        tmp_dir.mkdir(parents=True, exist_ok=True)
        print(tmp_dir)

        for url, hash in self.urls.items():
            file_name = Path(url).name
            file_path = tmp_dir / file_name
            if not file_path.exists():
                download_file(url, file_path, hash)

        try:
            return AtomsDataset(list(self.process(tmp_dir)))
        finally:
            if self.cleanup:
                shutil.rmtree(tmp_dir)


class SingleFileImporter(BaseImporter):
    def __init__(self, processing_dir: str, url: str, hash: str):
        super().__init__({url: hash}, processing_dir, cleanup=False)

    def process(self, tmp_dir: Path) -> Iterator[Atoms]:
        file_path = tmp_dir / Path(next(iter(self.urls))).name
        for atoms in self._read_file(file_path):
            yield self.process_atoms(atoms)

    def process_atoms(self, atoms: Atoms) -> Atoms:
        return atoms

    def _read_file(self, file_path: Path) -> Iterator[Atoms]:
        yield from ase.io.iread(file_path, index=":")
