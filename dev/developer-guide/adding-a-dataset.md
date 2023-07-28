Adding a dataset to `load-atoms` is relatively straightforward. 

In all cases, we need to add a metadata file to the `database` folder that describes the dataset and tells `load-atoms` where to find the structure files.

In some cases the structure files are hosted elsewhere (e.g. on Zenodo), in which case we only need to add the metadata file, otherwise we also need to upload the structure files to the `database` folder. These two cases share some steps, and then require different additional steps.

## Shared steps:

1. Create the file `database/<id>/<id>.yaml`, where `<id>` is the dataset ID.
2. Using e.g. the `database/C-GAP-17/C-GAP-17.yaml` file as a template, add the following essential information to the file:
    - `name`: The name of the dataset.
    - `description`: A description of the dataset.
3. You should also add other relevant information (see the [`DatasetInfo`](../../src/load_atoms/shared/dataset_info.py) class for a full list of optional parameters).
    - `license`: The license of the dataset.
    - `citation`: The citation for the dataset.


## Case 1: manually uploading a dataset

Example commits [SiO2-GAP-21](https://github.com/jla-gardner/load-atoms/commit/1e9fde32cc7e59c0ad3f720aba5c9764fa13bb48)

If the structure files are not hosted elsewhere, we need to upload them to the repo alongside the metadata file (see for instance [C-GAP-20.extxyz](database/C-GAP-20/C-GAP-20.extxyz)). A caveat here is that GitHub has a 100MB file size limit, so if the dataset is larger than this, we need to split it into multiple files (e.g. [C-SYNTH-1M](database/C-SYNTH-1M)). Ensure also that you respect any license requirements for the dataset when doing this.

1. Add the structure files to the `database/<id>` folder.
2. Run `python dev/scripts/filehash.py database/<id>/<file>` to generate the file hashes for the structure files.
3. Add the file hashes in the `database/<id>/<id>.yaml` file.


## Case 2: adding a dataset hosted elsewhere
See for instance [P-GAP-20.yaml](database/P-GAP-20/P-GAP-20.yaml).
1. Download the files and generate a hash for each: `python dev/scripts/filehash.py <path-to-files>`.
2. Add the URL slug to the `database/<id>/<id>.yaml` file (e.g. `url_root: https://zenodo.org/record/1234567/files`).
3. Add the file hashes in the `database/<id>/<id>.yaml` file, such that `f"{url_root}/{filename}"` is the URL for each file.


## Finally

First, we check that everything is valid and working:
```bash
pytest -k database
```

This should complain that documentation is missing for your dataset - we can fix that:
```bash
python dev/scripts/generate_page.py <id>
```

If everything is working (or it isn't and after reasonable effort you can't fix it), open a PR with your changes and we will review it. Once the PR is merged, the dataset will appear on the website and be available to download via `load_atoms.dataset`.
