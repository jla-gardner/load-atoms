from load_atoms.backend import _get_info, _load_dataset
from load_atoms.classes import Dataset


def load_dataset(name: str) -> Dataset:
    """Load a dataset by name."""

    dataset = _load_dataset(name)
    info = _get_info(name)

    atoms = sum(len(structure) for structure in dataset)

    print(
        f"""\
Loaded {info.name}, containing {len(dataset):,} structures and {atoms:,} atoms.
This dataset is licensed under {info.license}.\
    """
    )

    return dataset
