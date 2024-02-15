########
Database
########

:code:`load_atoms` maintains a database of (named) datasets for ease of use. 
These can be downloaded from the internet (and cached locally) using 
:func:`~load_atoms.load_dataset`.

The metadata of each dataset is stored as a :code:`.yaml` (see for instance
`C-GAP-17.yaml <https://github.com/jla-gardner/load-atoms/blob/main/database/C-GAP-17/C-GAP-17.yaml>`_)
These are converted to :class:`~load_atoms.database.DatabaseEntry` objects at runtime.

.. autoclass:: load_atoms.database.DatabaseEntry()
    :show-inheritance:
    :members:
    :exclude-members: model_config, model_fields