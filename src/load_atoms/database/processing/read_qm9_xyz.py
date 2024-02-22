from __future__ import annotations

from io import StringIO
from pathlib import Path

from ase import Atoms
from ase.io import read

PROPERTY_KEYS = "index A B C mu alpha homo lumo gap r2 zpve U0 U H G Cv".split()
assert len(PROPERTY_KEYS) == 16


def process(file: Path) -> list[Atoms]:
    """
    Read in a single XYZ file from the QM9 dataset, and return it
    as a list of a single Atoms object.

    See the original README for a specification of the format used:
    https://figshare.com/files/3195392
    """
    (
        n,
        property_values,
        *content,
        frequencies,
        smiles,
        inchi,
    ) = file.read_text().replace("*^", "e").splitlines()

    # ignore first "gdb" property
    property_values = [float(v) for v in property_values.split()[1:]]
    assert len(property_values) == 16
    properties: dict = dict(zip(PROPERTY_KEYS, property_values))

    frequencies = list(map(float, frequencies.split()))
    properties["frequencies"] = frequencies

    # molecule characterisation
    properties["smiles"] = smiles.split()[-1]
    properties["inchi"] = inchi.split()[-1]

    # fake an extxyz file and get ase to read it
    header = 'Properties=species:S:1:pos:R:3:partial_charges:R:1 pbc="F F F"'
    with StringIO("\n".join([n, header, *content])) as extxyz:
        atoms: Atoms = read(extxyz, 0, format="extxyz")  # type: ignore
    atoms.info = properties

    return [atoms]
