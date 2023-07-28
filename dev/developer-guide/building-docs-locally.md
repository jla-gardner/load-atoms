# Documentation

The `load-atoms` documentation is built using [Sphinx](https://www.sphinx-doc.org/en/master/), and hosted at [this page](https://jla-gardner.github.io/load-atoms/).

There are two stages to the build process:
1. The `dev/scripts/generate_page.py` script is used to programmatically generate the documentation pages for each dataset in the database.
2. Sphinx is used to build the documentation.

The first step is **slow**, and need not be repeated unless (a) a database changes, (b) a new dataset is added to the database, or (c) the documentation template changes.
As such, we commit and track each of the generated pages in the repository such that these need not be generated on each build, speeding up the CI/CD process.

The second step is **fast**, and generates the final `*.html` pages from the `*.rst` files. This step is performed on each build, and is what is used to generate the documentation on the [GitHub Pages](https://jla-gardner.github.io/load-atoms/) site.


## Building the documentation locally

See the developer [README](README.md) for instructions on how to set up your environment.
Once you have done this, you can build the documentation locally using:

```bash
sphinx-autobuild dev/docs/source dev/docs/build
```

This will start a local server, and automatically rebuild the documentation whenever a change is detected to the documentation source files.

## Adding/updating a dataset

If you have changed a single dataset, the documentation for that dataset can be regenerated using:

```bash
python dev/scripts/generate_page.py <dataset_id>
```

## Changing the documentation template

If all dataset pages need to be regenerated (e.g. the documentation template has changed), the documentation pages for all datasets can be regenerated using:

```bash
python dev/scripts/rebuild_all_docs.py
```