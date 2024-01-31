<div align="center">
    <a href="https://jla-gardner.github.io/load-atoms/">
        <img src="https://raw.githubusercontent.com/jla-gardner/load-atoms/main/docs/source/logo.svg" width="50%"/>
    </a>
</div>
    
---

<div align="center">
    <a href="https://github.com/jla-gardner/load-atoms/">
        <img src="https://img.shields.io/github/license/jla-gardner/load-atoms"/>
    </a>
    <a href="https://github.com/jla-gardner/load-atoms/actions/workflows/docs.yaml">
        <img src="https://github.com/jla-gardner/load-atoms/actions/workflows/docs.yaml/badge.svg?branch=main"/>
    </a>
    <a href="https://github.com/jla-gardner/load-atoms/actions/workflows/tests.yaml">
        <img src="https://github.com/jla-gardner/load-atoms/actions/workflows/tests.yaml/badge.svg?branch=main"/>
    </a>
    <a href="https://codecov.io/gh/jla-gardner/load-atoms">
        <img src="https://codecov.io/gh/jla-gardner/load-atoms/branch/main/graph/badge.svg?token=HCVF02CDHR"/>
    </a>
    <a href="https://pypi.org/project/load-atoms/">
        <img src="https://img.shields.io/pypi/v/load-atoms?color=blue&label=version&logo=python&logoColor=white"/>
    </a>
    <a href="https://pypi.org/project/load-atoms/">
        <img src="https://img.shields.io/badge/dcoumentation-live-green.svg"/>
    </a>
    <a href="https://jla-gardner.github.io/load-atoms/">
        <img src="https://img.shields.io/pypi/dw/load-atoms?color=lavender&label=installs&logo=python&logoColor=white"/>
    </a>
</div>

---

`load-atoms` is a Python package for Loading Open Access DAtasets for Atomistic Materials Science (LOAD-ATOMS).

> [!WARNING]
> This project is under active development. Until version 1.0.0 is released, breaking changes to the API may occur with no notice.

## Installation

`pip install load-atoms`

## Usage

```pycon
>>> from load_atoms import dataset
>>> structures = dataset("C-GAP-17")
Downloading C-GAP-17.extxyz
100.0% | ██████████████████████████████████████████████████
This dataset is covered by the CC BY-NC-SA 4.0 license.
Please cite this dataset if you use it in your work.
For more information about this dataset, see here:
https://jla-gardner.github.io/load-atoms/datasets/C-GAP-17.html
```

## Documentation

For more information, see the [documentation](https://jla-gardner.github.io/load-atoms/).

## Development

Please see the [contributing guidelines](https://raw.githubusercontent.com/jla-gardner/load-atoms/main/dev/devoloper-guide) for information on how to contribute to the project.
