from __future__ import annotations

from pathlib import Path
from typing import Iterator

import ase
import ase.io
from ase import Atoms
from load_atoms.database.backend import BaseImporter
from load_atoms.database.internet import FileDownload
from load_atoms.progress import Progress

_HASHES = {
    64: "25627b8c50d9",
    216: "da49808517c3",
    512: "654e2e1d1349",
    1000: "ae52f05f2231",
}


class Importer(BaseImporter):
    @classmethod
    def files_to_download(cls) -> list[FileDownload]:
        _base_url = (
            "https://github.com/lamr18/aSi-data/raw/refs/heads/main/data/xyz/"
        )

        return [
            FileDownload(
                url=f"{_base_url}{n}-atoms.xyz",
                expected_hash=hash,
            )
            for n, hash in _HASHES.items()
        ]

    @classmethod
    def get_structures(
        cls, tmp_dir: Path, progress: Progress
    ) -> Iterator[Atoms]:
        with progress.new_task("Parsing files", total=len(_HASHES)) as task:
            for n in _HASHES:
                path = tmp_dir / f"{n}-atoms.xyz"
                for atoms in ase.io.iread(path, index=":"):
                    del atoms.info["cell_origin"], atoms.info["config_type"]
                    yield atoms

                task.update(advance=1)
