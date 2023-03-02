import warnings
from pathlib import Path

import yaml

from load_atoms.util import DATASETS_DIR, get_dataset_file
from load_atoms.validation import (
    AllOf,
    AnyOf,
    BibTeX,
    Blueprint,
    FileHash,
    IsIn,
    Mapping,
    Optional,
    Required,
)

dataset_file_exists = lambda x: get_dataset_file(x).exists()
valid_licences = ["MIT", "CC-BY-4.0", "CC BY-NC-SA 4.0"]

DESCRIPTION_BLUEPRINT = Blueprint(
    # -----------------------
    # --- required fields ---
    # -----------------------
    Required("name", str),
    Required("description", str),
    # test that files is a mapping of files that exist to their hashes
    Required("files", Mapping(AllOf(str, dataset_file_exists), FileHash())),
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
    try:
        entry = DatasetDescription.from_file(file)
        DATASETS[entry.name] = entry
    except:
        # if all tests pass, then we will never hit this in production
        warnings.warn(f"Failed to load dataset from {file}")


def is_known_dataset(dataset_id: str) -> bool:
    """Check if a dataset is known."""
    return dataset_id in DATASETS


def get_description_of(dataset_id: str) -> DatasetDescription:
    """Get the database entry for a dataset."""
    assert is_known_dataset(dataset_id), f"Dataset {dataset_id} is not known."
    return DATASETS[dataset_id]


def print_info_for(dataset: DatasetDescription) -> None:
    """print description and any license/citation info for a dataset"""
    print(dataset.description)

    if dataset.license is not None:
        print("This dataset is licensed under", dataset.license.strip())

    if dataset.citation is not None:
        print("If you use this dataset, please cite the following:")
        print(dataset.citation.strip())
