from dataclasses import dataclass
from typing import Sequence

from ase import Atoms


@dataclass
class Info:
    name: str
    description: str
    citation: str = None
    license: str = None
    _download_url: str = None


Dataset = Sequence[Atoms]
