from __future__ import annotations

from pathlib import Path
from typing import Iterator

import numpy as np
from ase import Atoms
from ase.units import eV, kcal, mol
from load_atoms.database.backend import BaseImporter, unzip_file
from load_atoms.database.internet import FileDownload
from load_atoms.progress import Progress


class Importer(BaseImporter):
    @classmethod
    def files_to_download(cls) -> list[FileDownload]:
        return [
            FileDownload(
                url="https://figshare.com/ndownloader/files/23950376",
                expected_hash="cddeea2ec2c4",
                local_name="rmd17.tar.bz2",
            )
        ]

    @classmethod
    def get_structures(
        cls, tmp_dir: Path, progress: Progress
    ) -> Iterator[Atoms]:
        # Unzip the file
        contents_path = (
            unzip_file(tmp_dir / "rmd17.tar.bz2", progress) / "rmd17/npz_data"
        )

        # Process each npz archive
        structure_names = "aspirin benzene ethanol malonaldehyde naphthalene paracetamol salicylic toluene uracil azobenzene".split()  # noqa: E501
        assert len(structure_names) == 10

        for structure_name in structure_names:
            archive_path = contents_path / f"rmd17_{structure_name}.npz"
            archive = np.load(archive_path)
            Z = archive["nuclear_charges"]
            coords = archive["coords"]
            energy = archive["energies"]
            forces = archive["forces"]

            for idx in np.argsort(archive["old_indices"]):
                structure = Atoms(numbers=Z, positions=coords[idx])
                structure.info["name"] = structure_name
                structure.info["energy"] = energy[idx] / (kcal / mol) * eV
                structure.arrays["forces"] = forces[idx] / (kcal / mol) * eV
                yield structure
