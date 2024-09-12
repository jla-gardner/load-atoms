# explicitly not using future annotations since this is not supported
# by pydantic for python versions we want to target

from pathlib import Path
from typing import Dict, Literal, Optional, Union

import yaml
from pydantic import BaseModel, field_validator

from load_atoms.utils import BASE_REMOTE_URL

LICENSE_URLS = {
    "CC BY-NC-SA 4.0": "https://creativecommons.org/licenses/by-nc-sa/4.0/deed.en",
    "CC BY-NC 4.0": "https://creativecommons.org/licenses/by-nc/4.0/deed.en",
    "CC BY 4.0": "https://creativecommons.org/licenses/by/4.0/deed.en",
    "CC0": "https://creativecommons.org/publicdomain/zero/1.0/",
    "MIT": "https://opensource.org/licenses/MIT",
    "GPLv3": "https://www.gnu.org/licenses/gpl-3.0.html",
}
VALID_LICENSES = list(LICENSE_URLS.keys())

VALID_CATEGORIES = ["Benchmarks", "Potential Fitting", "Synthetic Data"]


class PropertyDescription(BaseModel):
    """
    Holds a description of a property, such that it can be automatically
    validated upon creation.
    """

    desc: str
    """A description of the property"""

    units: Optional[str] = None
    """The units of the property"""


class DatabaseEntry(BaseModel):
    """
    Holds all the required metadata for a named dataset, such that it can be
    automatically downloaded using :func:`~load_atoms.load_dataset`, and so that
    documentation can be automatically generated.
    """

    name: str
    """The name of the dataset"""

    year: int
    """The year the dataset was created"""

    description: str
    """A description of the dataset (in ``.rst`` format)"""

    category: str
    """
    The category of the dataset 
    (e.g. ``"Potential Fitting"``, ``"Benchmarks"``)
    """

    format: Literal["lmdb", "memory"] = "memory"
    """The format of the dataset"""

    minimum_load_atoms_version: Union[str, None] = None
    """
    The minimum version of load-atoms that is required to load the dataset.
    """

    citation: Optional[str] = None
    """A citation for the dataset (in BibTeX format)"""

    license: Optional[str] = None
    """The license identifier of the dataset (e.g. ``"CC BY-NC-SA 4.0"``)"""

    representative_structure: Optional[int] = None
    """The index of a representative structure (for visualisation purposes)"""

    per_atom_properties: Optional[Dict[str, PropertyDescription]] = None
    """A mapping from per-atom properties to their descriptions"""

    per_structure_properties: Optional[Dict[str, PropertyDescription]] = None
    """A mapping from per-structure properties to their descriptions"""

    @field_validator("category")
    def validate_category(cls, v):
        if v not in VALID_CATEGORIES:
            raise ValueError(
                f"Invalid category: {v}. Must be one of {VALID_CATEGORIES}"
            )
        return v

    @field_validator("license")
    def validate_license(cls, v):
        if v not in VALID_LICENSES:
            raise ValueError(
                f"Invalid license: {v}. Must be one of {VALID_LICENSES}"
            )
        return v

    @field_validator("citation")
    def validate_citation(cls, v):
        v = v.strip()
        if v.startswith("@") and v.endswith("}"):
            return v
        raise ValueError(f"Invalid BibTeX: {v}")

    @field_validator("minimum_load_atoms_version", mode="before")
    def convert_minimum_version_to_str(cls, v):
        if v is None:
            return None
        return str(v)

    @classmethod
    def from_yaml_file(cls, path: Union[Path, str]) -> "DatabaseEntry":
        path = Path(path).resolve()
        with open(path) as f:
            data = yaml.safe_load(f)

        try:
            return cls(**data)
        except Exception as e:
            raise ValueError(
                f"Error loading dataset description from {path}. It may be "
                "that you have a stale version of this dataset's yaml file on "
                "disk. Please delete the file and try again:\n"
                f'   $ rm "{path}"'
            ) from e

    @classmethod
    def remote_url_for_yaml(cls, dataset_id: str) -> str:
        return BASE_REMOTE_URL + f"{dataset_id}/{dataset_id}.yaml"

    @classmethod
    def importer_file_stem(cls, dataset_id: str) -> str:
        return dataset_id.lower().replace("-", "_")

    @classmethod
    def remote_url_for_importer(cls, dataset_id: str) -> str:
        fname = DatabaseEntry.importer_file_stem(dataset_id)
        return BASE_REMOTE_URL + f"src/load_atoms/database/importers/{fname}.py"
