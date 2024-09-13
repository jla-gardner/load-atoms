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
                url="https://zenodo.org/records/7704087/files/jla-gardner/carbon-data-v1.0.zip",
                expected_hash="b43fc702ef6d",
            )
        ]

    @classmethod
    def get_structures(
        cls, tmp_dir: Path, progress: Progress
    ) -> Iterator[Atoms]:
        # Unzip the file
        contents_path = unzip_file(tmp_dir / "carbon-data-v1.0.zip", progress)

        extxyz_files = sorted(contents_path.glob("**/*.extxyz"))
        task = progress.new_task(
            f"Processing {len(extxyz_files)} .extxyz files",
            total=len(extxyz_files),
        )

        # iterate through all .extxyz files
        for file_path in extxyz_files:
            structures = ase.io.read(file_path, index=":")
            assert isinstance(structures, list)
            for structure in structures:
                yield process_structure(structure)

            task.update(advance=1)


def process_structure(structure: Atoms) -> Atoms:
    structure = rename(
        structure,
        {
            "gap17_forces": "forces",
            "gap17_energy": "local_energies",
        },
    )
    structure.info["energy"] = structure.arrays["local_energies"].sum()
    return structure
