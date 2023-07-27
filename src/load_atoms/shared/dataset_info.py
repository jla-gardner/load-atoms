from pathlib import Path
from typing import Dict, List, Optional

import yaml
from pydantic import BaseModel, field_validator

from load_atoms.shared import BASE_REMOTE_URL
from load_atoms.shared.checksums import valid_checksum


class DatasetInfo(BaseModel):
    """
    Represents the metadata of a dataset. Anything information that
    is associated with a dataset (but not with a specific structure)
    should be stored here.

    This subclasses pydantic's BaseModel, which means that it can be
    it will be automatically validated when it is created.
    """

    name: str
    """the name of the dataset"""

    description: str
    """a short description of the dataset"""

    files: Dict[str, str]
    """a dictionary mapping file names to their checksums"""

    citation: Optional[str] = None
    """a BibTeX citation for the dataset"""

    license: Optional[str] = None
    """the license of the dataset"""

    representative_structures: Optional[List[int]] = None
    """a list of indices of representative structures"""

    long_description: Optional[str] = None
    """a longer description of the dataset"""

    per_atom_properties: Optional[dict] = None
    """a mapping of per atom property keys to a description"""

    per_structure_properties: Optional[dict] = None
    """a mapping of per structure property keys to a description"""

    url_root: Optional[str] = None
    """the root url of the dataset"""

    @field_validator("license")
    def validate_license(cls, v):
        valid_licences = ["MIT", "CC-BY-4.0", "CC BY-NC-SA 4.0"]
        if v not in valid_licences:
            raise ValueError(f"Invalid license: {v}. Must be one of {valid_licences}")
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

    @classmethod
    def from_yaml_file(cls, path: Path) -> "DatasetInfo":
        """
        Load dataset metadata from a .yaml description file.
        """
        with open(path) as f:
            data = yaml.safe_load(f)
        return cls(**data)

    def remote_file_locations(self) -> Dict[str, str]:
        """
        Mapping from remote file locations to their checksums.
        """
        base_url = self.url_root or BASE_REMOTE_URL + self.name + "/"
        return {base_url + k: v for k, v in self.files.items()}

    @classmethod
    def description_file_url(cls, dataset_id):
        """Get the URL for a dataset description file."""

        return BASE_REMOTE_URL + f"{dataset_id}/{dataset_id}.yaml"


DatasetId = str
