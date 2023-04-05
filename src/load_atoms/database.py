from pathlib import Path
from typing import Dict, List

import yaml
from pydantic import BaseModel, validator

from load_atoms.checksums import valid_checksum
from load_atoms.util import DATASETS_DIR


def is_bibtex(data: str) -> bool:
    data = data.strip()
    return data.startswith("@") and data.endswith("}")


class DatasetDescription(BaseModel):
    name: str
    description: str
    files: Dict[str, str]
    citation: str = None
    license: str = None
    representative_structures: List[int] = None
    long_description: str = None
    per_atom_properties: dict = None
    per_structure_properties: dict = None

    @validator("license")
    def validate_license(cls, v):
        valid_licences = ["MIT", "CC-BY-4.0", "CC BY-NC-SA 4.0"]
        if v not in valid_licences:
            raise ValueError(f"Invalid license: {v}. Must be one of {valid_licences}")
        return v

    @validator("files")
    def validate_files(cls, v):
        for data in v.values():
            if not valid_checksum(data):
                raise ValueError(f"Invalid checksum: {data}")
        return v

    @validator("citation")
    def validate_citation(cls, v):
        if not is_bibtex(v):
            raise ValueError(f"Invalid BibTeX: {v}")
        return v

    @classmethod
    def from_file(cls, path: Path) -> "DatasetDescription":
        with open(path) as f:
            data = yaml.safe_load(f)
        return cls(**data)


def find_all_descriptor_files() -> List[Path]:
    """Find all descriptor files."""

    return list(DATASETS_DIR.glob("**/*.yaml"))


def is_known_dataset(dataset_id: str) -> bool:
    """Check if a dataset is known."""
    return dataset_id in DATASETS


def get_description_of(dataset_id: str) -> DatasetDescription:
    """Get the database entry for a dataset."""
    assert is_known_dataset(dataset_id), f"Dataset {dataset_id} is not known."
    return DATASETS[dataset_id]


DATASETS = {}
for file in find_all_descriptor_files():
    entry = DatasetDescription.from_file(file)
    DATASETS[entry.name] = entry
