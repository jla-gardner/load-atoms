from typing import Iterable, List

from ase import Atoms
from yaml import dump


class Dataset:
    def __init__(self, structures: Iterable[Atoms], name: str = None):
        self.structures = [*structures]
        self.name = name

    def __len__(self):
        return len(self.structures)

    def __getitem__(self, slice):
        if isinstance(slice, int):
            return self.structures[slice]
        else:
            return Dataset(self.structures[slice])

    def __iter__(self):
        return iter(self.structures)

    def __repr__(self):
        return summarise_dataset(self.structures, self.name)


def intersection(things):
    return set.intersection(*map(set, things))


def summarise_dataset(structures: List[Atoms], name: str = None) -> str:
    N = len(structures)
    number_atoms = sum([len(structure) for structure in structures])

    per_atom_properties = intersection(
        structure.arrays.keys() for structure in structures
    )
    per_atom_properties -= {"numbers", "positions"}
    per_structure_properties = intersection(
        structure.info.keys() for structure in structures
    )

    species = intersection(structure.get_chemical_symbols() for structure in structures)
    species_counts = {
        s: sum([structure.get_chemical_symbols().count(s) for structure in structures])
        for s in species
    }
    species_counts = {k: f"{v / number_atoms:.2%}" for k, v in species_counts.items()}

    if N >= 1000:
        N = f"{N:,}"
    if number_atoms >= 1000:
        number_atoms = f"{number_atoms:,}"

    properties = {
        "counts": {
            "structures": N,
            "atoms": number_atoms,
        },
        "species": species_counts,
        "properties": {
            "per atom": "(" + ", ".join(per_atom_properties) + ")",
            "per structure": "(" + ", ".join(per_structure_properties) + ")",
        },
    }

    return dump({name if name else "Dataset": properties}, sort_keys=False, indent=4)
