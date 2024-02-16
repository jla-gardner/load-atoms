.. warning::

    Until version 1.0.0 of load-atoms is released, the internals that this
    guide described are subject to change.

Dataset Metadata
=====================

:code:`load-atoms` exposes the ability to download named datasets from the internet. 
The :class:`~load_atoms.database.DatabaseEntry` class defines a schema for 
the metadata of such named datasets.

Currently, the metadata for each database is stored in a :code:`.yaml` file, and hosted in our repo
on :ref:`GitHub <https://github.com/jla-gardner/load-atoms/blob/main/database/C-GAP-17/C-GAP-17.yaml>`.
The first time that :func:`~load_atoms.load_dataset` is called with a given dataset name, 
we attempt to download and parse this metadata file from the internet. 

Once we have a :class:`~load_atoms.database.DatabaseEntry` object, we can download the structures it describes.
**Currently**, each :class:`~load_atoms.database.DatabaseEntry` has a :code:`files` attribute, which
lists a collection of urls to download. We download all of these, cache them to disk, and read them.
**Currently**, :code:`load-atoms` only supports files that :func:`~ase.io.read` can read. This is liable to change
in the near future (i.e. support more file formats, and define optional pre-processing steps, for instance 
when downloading a :code:`.zip` file).

.. autoclass:: load_atoms.database.DatabaseEntry()
   :members:
   :exclude-members: __init__, model_config, model_fields


Docs
====

The :code:`load-atoms` package is documented using :code:`sphinx`. 
Per-dataset pages and information are automatically generated from the metadata files using scripts found in 
`dev/scripts <https://github.com/jla-gardner/load-atoms/tree/main/dev/scripts>`_.

To update the documentation to reflect changes to a single dataset, run:

.. code-block:: bash

    python dev/scripts/generate_page.py <dataset-id>

To update the documentation to reflect changes to all datasets, run:

.. code-block:: bash

    python dev/scripts/rebuild_all_docs.py

