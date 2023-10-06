import numpy as np
from ase import Atoms
from ase.io import write

rand = np.random.RandomState(42)

systems = (
    "aspirin benzene2017 ethanol malonaldehyde "
    "naphthalene salicylic toluene uracil"
).split()

all_structures = []

for system in systems:
    archive = np.load(f"md17/md17_{system}.npz")
    arrays = {name: archive[name] for name in archive.files}

    # randomly choose 1,200 structures: 1k train, 100 val, 100 test
    indices = rand.choice(len(arrays["E"]), size=1_200, replace=False)

    for i, idx in enumerate(indices):
        atoms = Atoms(
            numbers=arrays["z"],
            positions=arrays["R"][idx],
        )
        atoms.info["energy"] = arrays["E"][idx]
        atoms.info["split"] = (
            "train" if i < 1_000 else "val" if i < 1_100 else "test"
        )
        atoms.info["system"] = system.replace(
            "2017", ""
        )  # benzene2017 -> benzene
        atoms.arrays["forces"] = arrays["F"][idx]
        all_structures.append(atoms)


write("MD17-1k.extxyz", all_structures)
