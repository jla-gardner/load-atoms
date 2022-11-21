# Name?

-   chem_data
-   LOAD-AMM: Large Open Access Datasets for Atomistic Materials Modelling
-   LOAD-AtoMS: Large Open Access Datasets for Atomistic Materials Science

# Must Haves

Load datasets using a simple API.\
Behind the scenes, this should download the dataset and cache it to disk.

```python
from chem_data import load_dataset

dataset = load_dataset("C-GAP-17")
```

Basic functionality for doing cross-validation properly

```python
from chem_data import cross_validate

train, val, test = cross_validate(
    dataset,
    fold=0,
    folds=5,
    group_on="trajectory_id",
    ratio={"train": 8, "val": 1, "test": 1}
)
```

Readily accessible information about the dataset

```python
from chem_data import info

dataset_info = info("C-GAP-17")

print(dataset_info.name)
print(dataset_info.description)
print(dataset_info.citation)
print(dataset_info.url)
print(dataset_info.license)
```

# Nice to Haves

Easy data manipulations

```python
from chem_data import filter_by

bulk_amo = filter_by(dataset, config_type="bulk_amo")
large_structures = filter_by(dataset, lambda atoms: len(atoms) > 64)
```

Easy application of descriptors

```python
from chem_data import apply_descriptor
from quippy.descriptors import Descriptor

soap = Descriptor(
    "soap cutoff=3.0 cutoff_transition_width=1.0 "
    "n_max=8 l_max=6 atom_sigma=0.5"
)

descriptors = apply_descriptor(dataset, lambda atoms: soap.calc(atoms)['data'])
```

Summarise distribution of config types etc?
