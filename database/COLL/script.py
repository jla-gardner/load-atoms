from pathlib import Path

from ase.io import read, write
from load_atoms.backend.internet import download

splits = {
    "train": "https://figshare.com/ndownloader/files/25605734",
    "test": "https://figshare.com/ndownloader/files/25605737",
    "val": "https://figshare.com/ndownloader/files/25605740",
}

all_structures = []

for split, url in splits.items():
    path = Path(f"COLL-{split}.extxyz")
    if not path.exists():
        download(url, path)
    structures = read(path, index=":")
    for structure in structures:
        structure.info["split"] = split
        structure.calc = None
    all_structures.extend(structures)

# large file: split into 4
N = len(all_structures)
for i in range(4):
    write(
        f"COLL-{i}.extxyz",
        all_structures[i * N // 4 : (i + 1) * N // 4],
        format="extxyz",
    )
