# API

**Must be pip installable**

```bash
pip install load-atoms
```

**Downloading datasets should be easy and informative**

```ipython
In [1]: from load_atoms import dataset

In [2]: structures = dataset("C-GAP-17")
Downloading C-GAP-17 from github.com/vldgroup/load-atoms-data
100%|██████████████

This dataset is licensed under the CC-BY-4.0 license.
If you use this dataset, please cite the following:
"""
@article{Deringer-17,
    title = {Machine learning based interatomic potential for amorphous carbon},
    doi = {10.1103/PhysRevB.95.094203},
    volume = {95},
    number = {9},
    urldate = {2021-07-15},
    journal = {Physical Review B},
    author = {Deringer, Volker L. and Cs{\'a}nyi, G{\'a}bor},
    year = {2017},
    pages = {094203},
}
"""

In [3]: structures
Dataset:
    name: "C-GAP-17",
    counts:
        structures: 4,000
        atoms: 100,000
    species:
        C: 100%
    properties:
        per-structure: config_type, trajectory_id, energy
        per-atom: species, x, y, z, force
    info:
        Datset used to train the C-GAP-17 model, labelled with DFT
```

**Users should be able to wrap their own datasets**

```python
from load_atoms import dataset

structures = dataset([
    ase.Atoms("H2O"),
    ase.Atoms("H2O2")
])
```

**Datasets should behave indentically to lists of ASE atoms objects**

```python
data = dataset("100-C-structures")
train, test, val = data[:80], data[80:90], data[90:]
```

**Datsets should be easy to manipulate**

```python
from load_atoms import filter_by

bulk_amo = filter_bydata, config_type="bulk_amo")
large_structures = filter_by(data, lambda atoms: len(atoms) > 64)
```

```python
from load_atoms import cross_validate

train, val, test = cross_validate(
    dataset,
    fold=0,
    folds=5,
    group_on="trajectory_id",
    ratio={"train": 8, "val": 1, "test": 1}
)
```

# Website

-   readthedocs
-   contains API docs
-   contains examples
-   contains descriptions of and links to datasets

# Misc

-   Add a `load_atoms` command line tool
