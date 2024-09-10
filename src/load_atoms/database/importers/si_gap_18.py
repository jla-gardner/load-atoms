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
                    url="https://zenodo.org/record/1250555/files/libAtoms/silicon-testing-framework-v1.0.zip",
                    expected_hash="da0462802df1",
                    local_name="zip-file.zip",
                )
            ],
            cleanup=False,
        )

    def get_structures(
        self, tmp_dir: Path, progress: Progress
    ) -> Iterator[Atoms]:
        zip_file = tmp_dir / self.files_to_download[0].local_name

        # 1. unzip the file
        contents_path = unzip_file(zip_file, progress)

        # 2. read the xyz
        for structure in ase.io.iread(
            contents_path
            / "libAtoms-silicon-testing-framework-fc252cb/models/GAP/gp_iter6_sparse9k.xml.xyz"
        ):
            yield rename(
                structure,
                {
                    "DFT_force": "forces",
                    "dft_force": "forces",
                    "DFT_energy": "energy",
                    "dft_energy": "energy",
                },
            )
