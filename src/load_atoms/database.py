import warnings
from pathlib import Path

import yaml

from load_atoms.util import DATASETS_DIR
from load_atoms.validation import (
    BibTeX,
    Blueprint,
    FileHash,
    IsIn,
    Mapping,
    Optional,
    Required,
)

valid_licences = ["MIT", "CC-BY-4.0", "CC BY-NC-SA 4.0"]

DESCRIPTION_BLUEPRINT = Blueprint(
    # -----------------------
    # --- required fields ---
    # -----------------------
    Required("name", str),
    Required("description", str),
    # test that files is a mapping of files that exist to their hashes
    Required("files", Mapping(str, FileHash())),
    # -----------------------
    # --- optional fields ---
    # -----------------------
    Optional("citation", BibTeX()),
    Optional("license", IsIn(valid_licences)),
    Optional("representative_structures", [int]),
    Optional("long_description", str),
    Optional("per_atom_properties", dict),
    Optional("per_structure_properties", dict),
)


class DatasetDescription(DESCRIPTION_BLUEPRINT.dataclass()):
    @classmethod
    def from_file(cls, path: Path) -> "DatasetDescription":
        with open(path) as f:
            data = yaml.safe_load(f)

        return cls(**data)


_DESCRIPTOR_FILES = list(DATASETS_DIR.glob("**/*.yaml"))
DATASETS = {}
for file in _DESCRIPTOR_FILES:
    entry = DatasetDescription.from_file(file)
    DATASETS[entry.name] = entry


def is_known_dataset(dataset_id: str) -> bool:
    """Check if a dataset is known."""
    return dataset_id in DATASETS


def get_description_of(dataset_id: str) -> DatasetDescription:
    """Get the database entry for a dataset."""
    assert is_known_dataset(dataset_id), f"Dataset {dataset_id} is not known."
    return DATASETS[dataset_id]
