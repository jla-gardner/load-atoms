import numpy as np
from ase import Atoms
from ase.io import write

archive = {key: value for key, value in np.load("sn2_reactions.npz").items()}
structures = []

for i in range(len(archive["E"])):
    n_atoms = archive["N"][i]
    atoms = Atoms(
        positions=archive["R"][i][:n_atoms],
        numbers=archive["Z"][i][:n_atoms],
    )
    atoms.info = {
        "energy": archive["E"][i],
        "charge": archive["Q"][i],
        "dipole_moment": archive["D"][i],
    }
    atoms.arrays["forces"] = archive["F"][i][:n_atoms]

    structures.append(atoms)

# split in 4 equally sized files:
n = len(structures) // 4
for i in range(4):
    write(f"sn2_{i}.xyz", structures[i * n : (i + 1) * n])
