from dataclasses import dataclass
from pathlib import Path
from typing import List

import yaml

from load_atoms.util import DATASETS_DIR

from .validation import In, IsBibTeX, ListOf, OneOf, Optional, Required, Validator


@dataclass
class DatabaseEntry:
    name: str
    filenames: List[str]
    description: str
    citation: str = None
    license: str = None
    representative_structures: List[int] = None

    @classmethod
    def from_file(cls, file: Path):
        with open(file) as f:
            data = yaml.safe_load(f)

        if "filename" in data:
            data["filenames"] = [data["filename"]]
            del data["filename"]

        data = {k.replace(" ", "_"): v for k, v in data.items()}

        return cls(**data)


VALID_LICENSES = ["MIT", "CC-BY-4.0", "CC BY-NC-SA 4.0"]

VALIDATOR = Validator(
    # --- required fields ---
    Required("name", str),
    Required("description", str),
    OneOf(
        Required("filename", str),
        Required("filenames", ListOf(str)),
    ),
    # --- optional fields ---
    Optional("citation", IsBibTeX()),
    Optional("license", In(VALID_LICENSES)),
    Optional("representative structures", ListOf(int)),
    Optional("long description", str),
    Optional(
        "properties",
        Validator(
            Optional("per atom", dict),
            Optional("per structure", dict),
        ),
    ),
)


DATASETS = {
    entry.name: entry
    for entry in map(DatabaseEntry.from_file, DATASETS_DIR.glob("**/*.yaml"))
}


def is_known_dataset(dataset_id: str) -> bool:
    """Check if a dataset is known."""
    return dataset_id in DATASETS


def get_database_entry_for(dataset_id: str) -> DatabaseEntry:
    """Get the database entry for a dataset."""
    assert is_known_dataset(dataset_id), f"Dataset {dataset_id} is not known."
    return DATASETS[dataset_id]


def print_info_for(db_entry: DatabaseEntry) -> None:
    """print description and any license/citation info for a dataset"""
    print(db_entry.description)

    if db_entry.license is not None:
        print("This dataset is licensed under", db_entry.license.strip())

    if db_entry.citation is not None:
        print("If you use this dataset, please cite the following:")
        print(db_entry.citation.strip())
