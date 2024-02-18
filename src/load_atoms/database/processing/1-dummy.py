from __future__ import annotations

from pathlib import Path

from ase import Atoms


def process(x: Path) -> list[Atoms]:
    return [Atoms("H2O"), Atoms("H2O2")]
