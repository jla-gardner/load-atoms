from __future__ import annotations

from pathlib import Path
from typing import Iterator

from ase import Atoms
from ase.io import read
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
                    url="https://zenodo.org/records/7704087/files/jla-gardner/carbon-data-v1.0.zip",
                    expected_hash="b43fc702ef6d",
                )
            ]
        )

    def get_structures(
        self, tmp_dir: Path, progress: Progress
    ) -> Iterator[Atoms]:
        # Unzip the file
        contents_path = unzip_file(tmp_dir / "carbon-data-v1.0.zip")

        # Iterate through all .extxyz files
        for file_path in sorted(contents_path.glob("**/*.extxyz")):
            structures = read(file_path, index=":")
            for structure in structures:
                assert isinstance(structure, Atoms)
                structure = rename(
                    structure,
                    {
                        "gap17_forces": "forces",
                        "gap17_energy": "local_energies",
                    },
                )
                structure.info["energy"] = structure.arrays[
                    "local_energies"
                ].sum()
                yield structure
