from dataclasses import dataclass
from pathlib import Path

import yaml

from load_atoms.util import DATASETS_DIR
from load_atoms.validation import (
    AnyOf,
    Blueprint,
    IsBibTeX,
    IsIn,
    OneOf,
    Optional,
    Required,
)

VALID_LICENSES = ["MIT", "CC-BY-4.0", "CC BY-NC-SA 4.0"]

DESCRIPTION_BLUEPRINT = Blueprint(
    # --- required fields ---
    # -----------------------
    Required("name", str),
    Required("description", str),
    OneOf(
        Required("filename", str),
        Required("filenames", [str]),
    ),
    # --- optional fields ---
    # -----------------------
    Optional("citation", IsBibTeX()),
    Optional("license", IsIn(VALID_LICENSES)),
    Optional("representative_structures", [int]),
    Optional("long_description", str),
    Optional(
        "properties",
        AnyOf(
            Optional("per_atom", dict),
            Optional("per_structure", dict),
        ),
    ),
)


def preprocess_filename(data: dict) -> dict:
    """Convert filename to filenames."""

    if "filename" in data:
        assert "filenames" not in data
        data["filenames"] = [data.pop("filename")]
    return data


PRE_PROCESSORS = [preprocess_filename]


@dataclass
class DatasetDescription:
    name: str
    description: str
    filenames: list = None

    citation: str = None
    license: str = None
    representative_structures: list = None
    long_description: str = None
    properties: dict = None

    @classmethod
    def from_file(cls, path: Path) -> "DatasetDescription":
        with open(path) as f:
            data = yaml.safe_load(f)
        DESCRIPTION_BLUEPRINT.validate(data)

        for preprocessor in PRE_PROCESSORS:
            data = preprocessor(data)

        return cls(**data)


_descriptor_files = list(DATASETS_DIR.glob("**/*.yaml"))
DATASETS = {
    entry.name: entry for entry in map(DatasetDescription.from_file, _descriptor_files)
}


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
