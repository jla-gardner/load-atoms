

Building the Docs
=================

The :code:`load-atoms` package is documented using :code:`sphinx`. 
Per-dataset pages and information are automatically generated from the metadata files using scripts found in 
`dev/scripts <https://github.com/jla-gardner/load-atoms/tree/main/dev/scripts>`_.

To update the documentation to reflect changes to a single dataset, run:

.. code-block:: bash

    python dev/scripts/generate_page.py <dataset-id>

To update the documentation to reflect changes to all datasets, run:

.. code-block:: bash

    python dev/scripts/rebuild_all_docs.py

