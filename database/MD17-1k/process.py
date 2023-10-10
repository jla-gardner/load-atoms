import numpy as np
from ase import Atoms
from ase.io import write

kcal_per_mol_to_eV = 0.04336414
rand = np.random.RandomState(42)

systems = (
    "aspirin benzene2017 ethanol malonaldehyde "
    "naphthalene salicylic toluene uracil"
).split()

all_structures = []

for system in systems:
    archive = np.load(f"md17/md17_{system}.npz")
    arrays = {name: archive[name] for name in archive.files}

    # randomly choose 2_000 structures: 950 train, 50 val, 1k test
    indices = rand.choice(len(arrays["E"]), size=2_000, replace=False)

    for i, idx in enumerate(indices):
        atoms = Atoms(
            numbers=arrays["z"],
            positions=arrays["R"][idx],
        )
        atoms.info["energy"] = arrays["E"][idx] * kcal_per_mol_to_eV
        atoms.info["split"] = (
            "train" if i < 950 else "val" if i < 1_000 else "test"
        )
        atoms.info["system"] = system.replace(
            "2017", ""
        )  # benzene2017 -> benzene
        atoms.arrays["forces"] = arrays["F"][idx] * kcal_per_mol_to_eV
        all_structures.append(atoms)


write("MD17-1k.extxyz", all_structures)
