from dataclasses import asdict, dataclass
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
            Optional("per atom", dict),
            Optional("per structure", dict),
        ),
    ),
)


@dataclass
class DatasetDescription:
    name: str
    description: str
    filename: str = None
    filenames: list = None

    citation: str = None
    license: str = None
    representative_structures: list = None
    long_description: str = None
    properties: dict = None

    def __post_init__(self):
        # validate the data
        DESCRIPTION_BLUEPRINT.validate(asdict(self))

        # make sure we have a list of filenames
        if self.filename is not None:
            assert self.filenames is None
            self.filenames = [self.filename]

    @classmethod
    def from_file(cls, path: Path) -> "DatasetDescription":
        with open(path) as f:
            data = yaml.safe_load(f)
        DESCRIPTION_BLUEPRINT.validate(data)
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
