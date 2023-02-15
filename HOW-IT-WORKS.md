The purpose of this package is to make downloading datasets of ase structures as simple and easy as possible.

How does this work?

First, we keep copies of all the datasets in the `datasets` directory. Datasets are composed of two parts:

1. a `<dataset>.yaml` file, which contains the metadata for the dataset
2. one/several files containg the actual structures, in a format that can be read by ASE (e.g. `*.xyz`, `*.traj`)

We keep installation of this package light and quick by only downloading the `.yaml` file at install time. The actual structure files are downloaded (and subsequently cached locally) when the user first tries to access the dataset.

The main function of this package is the `dataset` function. This can be used in several ways:

-   to download a dataset from the internet:

    ```python
    from load_atoms import dataset

    data = dataset("100-C-structures")
    ```

-   to wrap a list of ASE atoms objects:

    ```python
    from load_atoms import dataset

    structures = dataset([
        ase.Atoms("H2O"),
        ase.Atoms("H2O2")
    ])
    ```

-   to load some structures from a local file:

    ```python
    from load_atoms import dataset

    structures = dataset("path/to/file.xyz")
    ```

The `Dataset` class instance behaves identically to a list of ASE atoms objects, and can be used in the same way. We use it so that we can print some nice information about it, and so that we can add some extra functionality in the future.
