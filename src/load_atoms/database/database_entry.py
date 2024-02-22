# explicitly not using future annotations since this is not supported
# by pydantic for python versions we want to target
from pathlib import Path
from typing import Callable, Dict, List, Optional, Union

import yaml
from ase import Atoms
from pydantic import BaseModel, field_validator

from load_atoms.progress import Progress
from load_atoms.utils import BASE_REMOTE_URL, valid_checksum

from .processing import default_processing, parse_steps

valid_licenses = {
    "CC BY-NC-SA 4.0": "https://creativecommons.org/licenses/by-nc-sa/4.0/deed.en",
    "CC BY-NC 4.0": "https://creativecommons.org/licenses/by-nc/4.0/deed.en",
    "CC BY 4.0": "https://creativecommons.org/licenses/by/4.0/deed.en",
    "CC0": "https://creativecommons.org/publicdomain/zero/1.0/",
    "MIT": "https://opensource.org/licenses/MIT",
    "GPLv3": "https://www.gnu.org/licenses/gpl-3.0.html",
}

valid_categories = ["Benchmarks", "Potential Fitting", "Synthetic Data"]


class PropertyDescription(BaseModel):
    """
    Holds a description of a property, such that it can be automatically
    validated upon creation.
    """

    desc: str
    """A description of the property"""

    units: Optional[str] = None
    """The units of the property"""


class FileInformation(BaseModel):
    """
    Holds metadata for a remote file

    Partial speficiation are allowed:

    Speficiations of the following form assume that the file is available at
    :code:`database/{name}/{filename}`.

    .. code-block:: yaml

        name: <filename>
        hash: <checksum>

    Speficiations of the following form assume that the :code:`filename`
    is the last part of the URL.

    .. code-block:: yaml

        url: <url>
        hash: <checksum>
    """

    name: str
    hash: str
    url: str

    @field_validator("hash")
    def validate_hash(cls, v):
        if not valid_checksum(v):
            raise ValueError(f"Invalid checksum: {v}")
        return v


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

    files: List[FileInformation]
    """
    A list of files that are part of the dataset, along with their checksums
    and URLs.
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

    per_atom_properties: Optional[Dict[str, PropertyDescription]] = None
    """A mapping from per-atom properties to their descriptions"""

    per_structure_properties: Optional[Dict[str, PropertyDescription]] = None
    """A mapping from per-structure properties to their descriptions"""

    processing: Callable[[Path, Progress], List[Atoms]]
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

    @field_validator("citation")
    def validate_citation(cls, v):
        v = v.strip()
        if v.startswith("@") and v.endswith("}"):
            return v
        raise ValueError(f"Invalid BibTeX: {v}")

    @classmethod
    def from_yaml_file(cls, path: Union[Path, str]) -> "DatabaseEntry":
        with open(path) as f:
            data = yaml.safe_load(f)

        # process defaults for file structure
        for file in data["files"]:
            if "url" not in file:
                file["url"] = BASE_REMOTE_URL + f"{data['name']}/{file['name']}"
            elif "name" not in file:
                file["name"] = file["url"].split("/")[-1]

        # parse processing : TODO: pydantic-ify this
        if "processing" in data:
            data["processing"] = parse_steps(data["processing"])
        else:
            files = data["files"]
            if not len(files) == 1:
                raise ValueError(
                    "If no processing is provided, the dataset must have "
                    "exactly one file."
                )
            data["processing"] = default_processing(files[0]["name"])

        try:
            return cls(**data)
        except Exception as e:
            raise ValueError(
                f"Error loading dataset description from {path}"
            ) from e

    @classmethod
    def remote_url_for(cls, dataset_id):
        return BASE_REMOTE_URL + f"{dataset_id}/{dataset_id}.yaml"
