# explicitly not using future annotations since this is not supported
# by pydantic for python versions we want to target
from pathlib import Path
from typing import Callable, Dict, List, Optional

import yaml
from ase import Atoms
from pydantic import BaseModel, field_validator

from load_atoms.utils import BASE_REMOTE_URL, valid_checksum

from .processing import default_processing, parse_steps

valid_licenses = {
    "CC BY-NC-SA 4.0": "https://creativecommons.org/licenses/by-nc-sa/4.0/deed.en",
    "CC BY-NC 4.0": "https://creativecommons.org/licenses/by-nc/4.0/deed.en",
    "CC BY 4.0": "https://creativecommons.org/licenses/by/4.0/deed.en",
    "MIT": "https://opensource.org/licenses/MIT",
}

valid_categories = ["Benchmarks", "Potential Fitting", "Synthetic Data"]


class DatabaseEntry(BaseModel):
    """
    Holds all the required metadata for a named dataset, such that it can be
    automatically downloaded using
    :func:`load_dataset(dataset_name) <load_atoms.load_dataset>`, and so that
    documentation can be automatically generated.

    Subclassing pydantic's BaseModel, which means that automatic
    validation occurs upon creation.
    """

    name: str
    """The name of the dataset"""

    year: int
    """The year the dataset was created"""

    description: str
    """A description of the dataset (in :code:`.rst` format)"""

    files: Dict[str, str]
    """
    A mapping from file names to their checksums 
    (used for download validation purposes)
    """

    category: str
    """
    The category of the dataset 
    (e.g. :code:`"Potential Fitting"`, :code:`"Benchmarks"`)
    """

    citation: Optional[str] = None
    """A citation for the dataset (in BibTeX format)"""

    license: Optional[str] = None
    """The license identifier of the dataset (e.g. :code:`"CC BY-NC-SA 4.0"`)"""

    representative_structure: Optional[int] = None
    """The index of a representative structure (for visualisation purposes)"""

    per_atom_properties: Optional[dict] = None
    """A mapping from per-atom properties to their descriptions"""

    per_structure_properties: Optional[dict] = None
    """A mapping from per-structure properties to their descriptions"""

    url_root: Optional[str] = None
    """The root url of the dataset, at which all :code:`files` are located"""

    processing: Callable[[Path], List[Atoms]]
    """
    A function to turn the root downloaded path into the dataset's structures
    """

    @field_validator("category")
    def validate_category(cls, v):
        if v not in valid_categories:
            raise ValueError(
                f"Invalid category: {v}. Must be one of {valid_categories}"
            )
        return v

    @field_validator("license")
    def validate_license(cls, v):
        if v not in valid_licenses:
            raise ValueError(
                f"Invalid license: {v}. Must be one of {list(valid_licenses)}"
            )
        return v

    @field_validator("files")
    def validate_files(cls, v):
        for data in v.values():
            if not valid_checksum(data):
                raise ValueError(f"Invalid checksum: {data}")
        return v

    @field_validator("citation")
    def validate_citation(cls, v):
        v = v.strip()
        if v.startswith("@") and v.endswith("}"):
            return v
        raise ValueError(f"Invalid BibTeX: {v}")

    @field_validator("url_root")
    def validate_url_root(cls, v):
        if v is not None and not v.endswith("/"):
            return v + "/"
        return v

    @classmethod
    def from_yaml_file(cls, path: Path) -> "DatabaseEntry":
        with open(path) as f:
            data = yaml.safe_load(f)
        if "processing" in data:
            data["processing"] = parse_steps(data["processing"])
        else:
            data["processing"] = default_processing()
        try:
            return cls(**data)
        except Exception as e:
            raise ValueError(
                f"Error loading dataset description from {path}"
            ) from e

    def remote_location(self, file: str) -> str:
        base_url = self.url_root or BASE_REMOTE_URL + self.name + "/"
        return base_url + file

    @classmethod
    def remote_url_for(cls, dataset_id):
        return BASE_REMOTE_URL + f"{dataset_id}/{dataset_id}.yaml"
