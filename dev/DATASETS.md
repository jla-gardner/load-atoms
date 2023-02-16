# How to add a dataset

This project is designed to be as easy as possible to add new datasets to. To add a new dataset, you need to do the following:

## 1. Add a `<dataset>.yaml` file in the `load_atoms/datasets` directory

This file should contain the following fields:

-   `name`: The name of the dataset. This should be a unique, preferably short and easily readable identifier for the dataset
-   `description`: A short description of the dataset, how it was generated etc.
-   `filename` or `filenames`: The name of the file(s) containing the dataset, relative to the `load_atoms/datasets` directory. If the dataset is split into multiple files, you can specify a list of filenames here. These can be nested inside directories, e.g. `my-dataset/atoms.xyz`.

Optionally, you can also specify the following fields:

-   `license`: The license under which the dataset is released.
-   `citation`: A citation for the dataset, if applicable. This should be a BibTeX citation.
-   `representative structures`: a list of structures that are representative of the dataset. The first 5 of these will be used to generate the dataset thumbnail on the documentation website.

Example:

```yaml
# load_atoms/datasets/my-dataset.yaml

name: my-dataset
description: A dataset of 1000 atoms
filename: my-dataset.xyz
license: MIT
citation: |
    @article{my-dataset,
        title={My dataset},
        author={John Doe},
        journal={arXiv:2101.00000},
        year={2021}
    }
```

## 2. Add the relevant data files

Bare in mind that GitHub has a 100MB file size limit, so if your dataset is larger than this, you will need to split it into multiple files. All of these files should be placed in the `load_atoms/datasets` directory, at relative paths specified in the `<dataset>.yaml` file.

## 3. Test that your dataset entry is valid can be loaded

To test that your dataset entry is valid, you can run the following command in the root directory of the project:

```bash
pytest -k test_database
```

## 4. Build the documentation

We add information about the datasets to the documentation, so that users can easily find them. To do this, you need to run the following command in the root directory of the project:

```bash
python dev/generate_page.py <new-dataset-id>
```
