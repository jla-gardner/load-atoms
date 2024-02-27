from __future__ import annotations

from io import StringIO
from pathlib import Path

from ase import Atoms
from ase.io import read
from ase.units import Hartree, eV

PROPERTY_KEYS = "index A B C mu alpha homo lumo gap r2 zpve U0 U H G Cv".split()
assert len(PROPERTY_KEYS) == 16
RESCALINGS = [1.0] * 16
for property in "homo lumo gap zpve U0 U H G".split():
    # convert from Hartree to eV
    RESCALINGS[PROPERTY_KEYS.index(property)] = Hartree / eV

# taken from https://figshare.com/ndownloader/files/3195395
OFFSET_COLUMNS = "U0 U H G".split()
OFFSETS = {
    "H": [-0.5002730, -0.4988570, -0.4979120, -0.5109270],
    "C": [-37.846772, -37.845355, -37.844411, -37.861317],
    "N": [-54.583861, -54.582445, -54.581501, -54.598897],
    "O": [-75.064579, -75.063163, -75.062219, -75.079532],
    "F": [-99.718730, -99.717314, -99.716370, -99.733544],
}

# taken from https://figshare.com/ndownloader/files/3195404
BAD_IDS = [
    int(id)
    for id in (Path(__file__).parent.resolve() / "bad_qm9.txt")
    .read_text()
    .splitlines()
]


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

    # fake an extxyz file and get ase to read it
    header = 'Properties=species:S:1:pos:R:3:partial_charges:R:1 pbc="F F F"'
    with StringIO("\n".join([n, header, *content])) as extxyz:
        atoms: Atoms = read(extxyz, 0, format="extxyz")  # type: ignore

    # ignore first "gdb" property
    property_values = [float(v) for v in property_values.split()[1:]]
    property_values[0] = int(property_values[0])
    # if property_values[0] in BAD_IDS:

    assert len(property_values) == 16
    properties: dict = dict(zip(PROPERTY_KEYS, property_values))

    for name in properties:
        if name in OFFSET_COLUMNS:
            for atom in atoms:
                properties[name] -= OFFSETS[atom.symbol][  # type: ignore
                    OFFSET_COLUMNS.index(name)
                ]
        properties[name] *= RESCALINGS[PROPERTY_KEYS.index(name)]

    properties["frequencies"] = list(map(float, frequencies.split()))

    # molecule characterisation
    properties["smiles"] = smiles.split()[-1]
    properties["inchi"] = inchi.split()[-1]
    properties["geometry"] = property_values[0] not in BAD_IDS

    atoms.info = properties

    return [atoms]
