
Dataset Loading
===============

:code:`load-atoms` exposes the ability to download named datasets from the internet. 
The :class:`~load_atoms.database.DatabaseEntry` class defines a schema for 
the metadata of such named datasets. These are serialised as a :code:`.yaml` file for each dataset,
and hosted in our repo on `GitHub <https://github.com/jla-gardner/load-atoms/blob/main/database/C-GAP-17/C-GAP-17.yaml>`_.

Loading a dataset by name is handled within :func:`load_structures(name, root) <load_atoms.database.backend.load_structures>`. 
Calling this function for the first time will trigger the following steps:

1. We donwload the associated :class:`~load_atoms.database.DatabaseEntry` 
   file to :code:`root/name/name.yaml`. 
2. Each :class:`~load_atoms.database.DatabaseEntry` object has a :code:`files` attribute, 
   which maps a collection of urls for download to their checksums. 
   We download all of these to a temporary directory, and validate them.
3. Each :class:`~load_atoms.database.DatabaseEntry` defines a procedure, :code:`processing`, that maps
   the root folder of the downloaded files to a list of :class:`~ase.Atoms` objects.
   If not explicitly defined, the default procedure is to read all files 
   in the root directory using :func:`~ase.io.read`. For more details, see :doc:`dataset-processing`.
4. We cache the list of :class:`~ase.Atoms` objects to :code:`root/name/name.xyz`, 
   and return the list.

Subsequent calls to :func:`~load_atoms.database.backend.load_structures` with the same dataset name will
simply read the cached :class:`~ase.Atoms` objects from :code:`root/name/name.xyz`.


.. autofunction:: load_atoms.database.backend.load_structures

.. autoclass:: load_atoms.database.DatabaseEntry()
   :members:
   :exclude-members: __init__, model_config, model_fields

