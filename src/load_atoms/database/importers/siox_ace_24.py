from pathlib import Path
from typing import Iterator

import ase.io
from ase import Atoms
from load_atoms.database.importer import (
    BaseImporter,
    FileDownload,
    rename,
    unzip_file,
)
from load_atoms.progress import Progress


class Importer(BaseImporter):
    def __init__(self):
        super().__init__(
            files_to_download=[
                FileDownload(
                    url="https://zenodo.org/records/10419194/files/database.zip",
                    expected_hash="42eb5808b0aa",
                )
            ],
        )

    def get_structures(
        self, tmp_dir: Path, progress: Progress
    ) -> Iterator[Atoms]:
        # unzip
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
