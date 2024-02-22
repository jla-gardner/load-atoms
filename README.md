> [!WARNING]
> This project is under active development. Until version 1.0.0 is released, breaking changes to the API may occur with no notice.
> 
<div align="center">
    <a href="https://jla-gardner.github.io/load-atoms/">
        <img src="https://raw.githubusercontent.com/jla-gardner/load-atoms/main/docs/source/logo.svg" width="50%"/>
    </a>
</div>
    
</br>

<div align="center">
    
[![PyPI](https://img.shields.io/pypi/v/load-atoms)](https://pypi.org/project/load-atoms/)
[![GitHub](https://img.shields.io/badge/license-MIT-blue)](LICENSE)
[![](https://github.com/jla-gardner/load-atoms/actions/workflows/tests.yaml/badge.svg?branch=main)](https://github.com/jla-gardner/load-atoms/actions/workflows/tests.yaml)
[![codecov](https://codecov.io/gh/jla-gardner/load-atoms/branch/main/graph/badge.svg)](https://codecov.io/gh/jla-gardner/load-atoms)
[![Documentation Status](https://img.shields.io/badge/documentation-live-green.svg)](https://jla-gardner.github.io/load-atoms/)
[![GitHub last commit](https://img.shields.io/github/last-commit/jla-gardner/load-atoms)]()

</div>

</br>

**`load-atoms`** is a Python package for **L**oading **O**pen **A**ccess **D**atasets for **Ato**mistic **M**aterials **S**cience (LOAD-AtoMS). 
See the [documentation](https://jla-gardner.github.io/load-atoms/) for more information.

**`load-atoms`** is maintained by me, John Gardner ([GitHub](https://github.com/jla-gardner) - [website](https://jla-gardner.github.io)), as part of my PhD research activities within the [Deringer Group](https://www.chem.ox.ac.uk/people/volker-deringer/).

## Installation

`pip install load-atoms`

## Usage


```pycon
>>> from load_atoms import load_dataset
>>> dataset = load_dataset("C-GAP-17")

╭─────────────────────────── C-GAP-17 ────────────────────────────╮
│                                                                 │
│  ✓  Downloading C-GAP-17.extxyz ━━━━━━━━━━━━━━━━━━━━ 100% 00:00 │
│  ✓  Reading C-GAP-17.extxyz     ━━━━━━━━━━━━━━━━━━━━ 100% 00:01 │
│  ✓  Caching to disk             ━━━━━━━━━━━━━━━━━━━━ 100% 00:00 │
│                                                                 │
│ The C-GAP-17 dataset is covered by the CC BY-NC-SA 4.0 license. │
│  Please cite the C-GAP-17 dataset if you use it in your work.   │
│     For more information about the C-GAP-17 dataset, visit      │
│                       load-atoms/C-GAP-17                       │
╰─────────────────────────────────────────────────────────────────╯
```

```
>>> print(dataset)

C-GAP-17:
    structures: 4,530
    atoms: 284,965
    species:
        C: 100.00%
    properties:
        per atom: (force)
        per structure: (config_type, detailed_ct, energy, split)
```


## Development

Please see the [contributing guidelines](https://jla-gardner.github.io/load-atoms/dev/developer-guide.html) for information on how to contribute to the project.
