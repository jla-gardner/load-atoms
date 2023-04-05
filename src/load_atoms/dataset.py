from pathlib import Path
from typing import Iterable, List

from ase import Atoms
from ase.io import read
from yaml import dump

from load_atoms import backend
from load_atoms.database import DATASETS, DatasetDescription, is_known_dataset
from load_atoms.util import frontend_url, intersection, union


class Dataset:
    def __init__(
        self, structures: Iterable[Atoms], description: DatasetDescription = None
    ):
        self.structures = [*structures]
        self._description = description

    def __len__(self):
        return len(self.structures)

    def __getitem__(self, slice):
        if isinstance(slice, int):
            # return a single structure
            return self.structures[slice]
        else:
            # return a new Dataset
            return Dataset(self.structures[slice])

    def __iter__(self):
        return iter(self.structures)

    def __repr__(self):
        return summarise_dataset(self.structures, self._description)

    @classmethod
    def from_structures(cls, structures: Iterable[Atoms]):
        return cls(structures)

    @classmethod
    def from_file(cls, path: Path):
        structures = read(path, index=":")
        return cls(structures, path.stem)

    @classmethod
    def from_id(cls, dataset_id: str, root: Path = None, verbose: bool = True):
        if not is_known_dataset(dataset_id):
            raise ValueError(f"Dataset {dataset_id} is not known.")
        dataset_info = DATASETS[dataset_id]
        all_structures = backend.get_structures(dataset_info, root)
        if verbose:
            print(usage_info(dataset_info))
        return cls(all_structures, dataset_info)

    @classmethod
    def from_structures(cls, structures: Iterable[Atoms]):
        return cls(structures)

    @classmethod
    def from_file(cls, path: Path):
        structures = read(path, index=":")
        return cls(structures, path.stem)


def usage_info(dataset: DatasetDescription) -> str:
    info = []
    if dataset.license is not None:
        info.append(f"This dataset is covered by the {dataset.license} license.")
    if dataset.citation is not None:
        info.append(f"Please cite this dataset if you use it in your work.")

    _url = frontend_url(dataset)
    info.append(f"For more information about this dataset, see here {_url}")

    return "\n".join(info)


def summarise_dataset(
    structures: List[Atoms], description: DatasetDescription = None
) -> str:

    name = description.name if description is not None else "Dataset"
    N = len(structures)
    number_atoms = sum([len(structure) for structure in structures])

    per_atom_properties = intersection(
        structure.arrays.keys() for structure in structures
    )
    per_atom_properties -= {"numbers", "positions"}
    per_structure_properties = intersection(
        structure.info.keys() for structure in structures
    )

    species = union(structure.get_chemical_symbols() for structure in structures)
    species_counts = {
        s: sum([structure.get_chemical_symbols().count(s) for structure in structures])
        for s in species
    }
    species_counts = {
        k: f"{v / number_atoms:.2%}"
        for k, v in sorted(
            species_counts.items(), key=lambda item: item[1], reverse=True
        )
    }

    if N >= 1000:
        N = f"{N:,}"
    if number_atoms >= 1000:
        number_atoms = f"{number_atoms:,}"

    fields = {
        "structures": N,
        "atoms": number_atoms,
        "species": species_counts,
        "properties": {
            "per atom": "(" + ", ".join(per_atom_properties) + ")",
            "per structure": "(" + ", ".join(per_structure_properties) + ")",
        },
    }

    return dump({name: fields}, sort_keys=False, indent=4)
