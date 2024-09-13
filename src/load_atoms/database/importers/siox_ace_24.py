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
                url="https://zenodo.org/records/10419194/files/database.zip",
                expected_hash="42eb5808b0aa",
            )
        ]

    @classmethod
    def get_structures(
        cls, tmp_dir: Path, progress: Progress
    ) -> Iterator[Atoms]:
        contents = unzip_file(tmp_dir / "database.zip", progress)
        for structure in ase.io.iread(
            contents / "database/training.general_purpose.SiOx.xyz"
        ):
            yield rename(
                structure,
                {
                    "dft_forces": "forces",
                    "dft_energy": "energy",
                    "dft_free_energy": "free_energy",
                    "dft_stress": "stress",
                    "dft_virials": "virial",
                },
            )
