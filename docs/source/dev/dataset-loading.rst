Dataset Loading
===============

:code:`load-atoms` exposes the ability to download named datasets from the internet. 
The :class:`~load_atoms.database.DatabaseEntry` class defines a schema for 
the metadata of such named datasets. These are serialised as a :code:`.yaml` file for each dataset,
and hosted in our repo on `GitHub <https://github.com/jla-gardner/load-atoms/blob/main/database/C-GAP-17/C-GAP-17.yaml>`_.

Loading a dataset by name is handled within :func:`~load_atoms.database.backend.load_dataset`. 
Calling this function for the first time will trigger the following steps:

1. We download the associated :class:`~load_atoms.database.DatabaseEntry` 
   file to :code:`root/name/name.yaml`.
2. We check if the dataset is compatible with the current version of load-atoms.
3. If the dataset hasn't been cached yet:
   a. We download and execute a dataset-specific importer script.
   b. The importer is responsible for downloading and processing the raw data files.
   c. The importer returns an :class:`~load_atoms.atoms_dataset.AtomsDataset` object.
4. We cache the :class:`~load_atoms.atoms_dataset.AtomsDataset` object to :code:`root/name/name.pkl`.
5. We display usage information, including license and citation details.

Subsequent calls to :func:`~load_atoms.database.backend.load_dataset` with the same dataset name will
simply read the cached :class:`~load_atoms.atoms_dataset.AtomsDataset` object from :code:`root/name/name.pkl`.


.. autofunction:: load_atoms.database.backend.load_dataset

.. autoclass:: load_atoms.database.DatabaseEntry()
   :members:
   :exclude-members: __init__, model_config, model_fields

