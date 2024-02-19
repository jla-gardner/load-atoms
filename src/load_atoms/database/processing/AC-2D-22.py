from __future__ import annotations

from pathlib import Path

from ase import Atoms
from ase.io import read

from load_atoms.database.processing import UnZip


def process(root: Path) -> list[Atoms]:
    """
    Read out the AC-2D-22 dataset from the downloaded Zenodo archive.
    """
    root = UnZip()(root)
    root = root / "data/fig_3"

    def read_structures(archive_dir) -> list[Atoms]:
        extracted = UnZip(file="fin_run.tar.gz")(archive_dir)
        return [read(file) for file in sorted(extracted.glob("**/*.xyz"))]  # type: ignore

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

    all_structures: list[Atoms] = []

    for path, info in table:
        structures = read_structures(root / path)
        for structure in structures:
            structure.info = info
        all_structures.extend(structures)

    renaming = {
        "Forces": "forces",
        "Energy_per_atom": "local_energy",
        "NN_Energy_per_atom": "nn_local_energy",
    }
    drop = ["c_1"]

    for structure in all_structures:
        for old, new in renaming.items():
            structure.arrays[new] = structure.arrays.pop(old)
        for key in drop:
            del structure.arrays[key]
        # rotate 90 degrees around the x-axis
        structure.rotate(90, "x", center="COU", rotate_cell=True)

    return all_structures
