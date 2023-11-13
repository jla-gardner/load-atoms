from pathlib import Path

import numpy as np
from ase.io import read, write

root_dir = Path("poet/poet_run/data/DFT_Cu/")
config_types = {
    "lowIndexSurfaces": "low-index-surfaces",
    "NPT_FCC_1400K": "npt-fcc-1400K",
    "NVT_FCC_300K": "nvt-fcc-300K",
    "NVT_FCC_1400K": "nvt-fcc-1400K",
}

all_structures = []

for config_type, config_type_name in config_types.items():
    dir = root_dir / config_type
    structures = [
        read(file)
        for file in sorted(dir.glob("*.vasp"), key=lambda file: int(file.stem))
    ]

    energies = map(float, (dir / "E0.data").read_text().splitlines())

    for structure, energy in zip(structures, energies):
        structure.info["energy"] = energy
        structure.info["config_type"] = config_type_name

    raw_stresses = (dir / "F_Cell.data").read_text().splitlines()

    for structure, raw_stress in zip(structures, raw_stresses):
        xx, yy, zz, xy, yz, zx = list(map(float, raw_stress.split()))
        structure.info["stress"] = np.array(
            [[xx, xy, zx], [xy, yy, yz], [zx, yz, zz]]
        )

    raw_forces = (dir / "F_coord.data").read_text().splitlines()
    # take the last 3 columns
    forces = np.array(
        [list(map(float, line.split()[-3:])) for line in raw_forces]
    )

    i = 0
    for structure in structures:
        structure.arrays["forces"] = forces[i : i + len(structure)]
        i += len(structure)

    all_structures.extend(structures)


write("Cu-POET.extxyz", all_structures)
