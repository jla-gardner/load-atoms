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
                url="https://zenodo.org/record/1250555/files/libAtoms/silicon-testing-framework-v1.0.zip",
                expected_hash="da0462802df1",
                local_name="zip-file.zip",
            )
        ]

    @classmethod
    def get_structures(
        cls, tmp_dir: Path, progress: Progress
    ) -> Iterator[Atoms]:
        contents_path = unzip_file(tmp_dir / "zip-file.zip", progress)

        for structure in ase.io.iread(
            contents_path
            / "libAtoms-silicon-testing-framework-fc252cb/models/GAP/gp_iter6_sparse9k.xml.xyz"  # noqa: E501
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
