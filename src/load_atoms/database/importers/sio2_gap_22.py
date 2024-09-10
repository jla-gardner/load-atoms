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
                    url="https://zenodo.org/records/6353684/files/sio2_potential_data.zip",
                    expected_hash="98ea6e58f6d9",
                )
            ],
        )

    def get_structures(
        self, tmp_dir: Path, progress: Progress
    ) -> Iterator[Atoms]:
        # unzip
        contents = unzip_file(tmp_dir / "sio2_potential_data.zip", progress)

        for structure in ase.io.iread(
            contents / "sio2_potential_data/database/dataset.scan.2.xyz"
        ):
            yield rename(structure, {"virials": "virial"})
