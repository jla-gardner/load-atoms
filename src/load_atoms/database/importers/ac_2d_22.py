from __future__ import annotations

from pathlib import Path
from typing import Iterator

from ase import Atoms
from ase.io import read
from load_atoms.database.backend import BaseImporter, rename, unzip_file
from load_atoms.database.internet import FileDownload
from load_atoms.progress import Progress


class Importer(BaseImporter):
    @classmethod
    def files_to_download(cls) -> list[FileDownload]:
        return [
            FileDownload(
                url="https://zenodo.org/record/7221166/files/data.tar.gz",
                expected_hash="023de5805f15",
            )
        ]

    @classmethod
    def get_structures(
        cls, tmp_dir: Path, progress: Progress
    ) -> Iterator[Atoms]:
        # untar the file
        contents_path = unzip_file(tmp_dir / "data.tar.gz", progress)
        root = contents_path / "data/fig_3"

        table = [
            (
                "loc_run_fig_3a/Final_structures",
                {
                    "config": "continuous random network",
                    "beta": 2.0,
                    "criterion": "local energy",
                },
            ),
            (
                "NN_run_fig_3b/Final_structures_pristine",
                {
                    "config": "paracrystalline",
                    "beta": 2.0,
                    "criterion": "nearest-neighbour energy",
                },
            ),
            (
                "NN_run_fig_3b/Final_structures_thermal",
                {
                    "config": "paracrystalline",
                    "beta": 2.0,
                    "criterion": "nearest-neighbour energy",
                },
            ),
            (
                "loc_run_fig_3c/beta_50/Final_structures",
                {
                    "config": "paracrystalline",
                    "beta": 50.0,
                    "criterion": "local energy",
                },
            ),
            (
                "loc_run_fig_3c/beta_60/Final_structures",
                {
                    "config": "paracrystalline",
                    "beta": 60.0,
                    "criterion": "local energy",
                },
            ),
            (
                "fig_3d/total_beta_0.8/Final_structures",
                {
                    "config": "paracrystalline",
                    "beta": 0.8,
                    "criterion": "total energy",
                },
            ),
        ]

        for path, info in table:
            structures = cls.read_structures(root / path, progress)
            for structure in structures:
                structure.info.update(info)
                yield cls.process_structure(structure)

    @staticmethod
    def read_structures(archive_dir: Path, progress: Progress) -> list[Atoms]:
        extracted = unzip_file(archive_dir / "fin_run.tar.gz", progress)
        return [read(file) for file in sorted(extracted.glob("**/*.xyz"))]  # type: ignore

    @staticmethod
    def process_structure(structure: Atoms) -> Atoms:
        # Remove unwanted arrays
        if "c_1" in structure.arrays:
            del structure.arrays["c_1"]

        # Rotate 90 degrees around the x-axis
        structure.rotate(90, "x", center="COU", rotate_cell=True)

        return rename(
            structure,
            {
                "Forces": "forces",
                "Energy_per_atom": "local_energy",
                "NN_Energy_per_atom": "nn_local_energy",
            },
        )
