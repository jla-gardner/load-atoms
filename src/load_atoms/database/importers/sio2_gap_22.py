from __future__ import annotations

from pathlib import Path
from typing import Iterator

import ase.io
from ase import Atoms
from load_atoms.database.backend import BaseImporter, rename, unzip_file
from load_atoms.database.internet import FileDownload
from load_atoms.progress import Progress


class Importer(BaseImporter):
    @classmethod
    def files_to_download(cls) -> list[FileDownload]:
        return [
            FileDownload(
                url="https://zenodo.org/records/6353684/files/sio2_potential_data.zip",
                expected_hash="98ea6e58f6d9",
            )
        ]

    @classmethod
    def get_structures(
        cls, tmp_dir: Path, progress: Progress
    ) -> Iterator[Atoms]:
        contents = unzip_file(tmp_dir / "sio2_potential_data.zip", progress)

        for structure in ase.io.iread(
            contents / "sio2_potential_data/database/dataset.scan.2.xyz"
        ):
            yield rename(structure, {"virials": "virial"})
