####################
:code:`AtomsDataset`
####################

The core class of :code:`load-atoms` is the :class:`~load_atoms.AtomsDataset` class. 
To create such a dataset, use the :func:`~load_atoms.load_dataset` function.

.. autoclass:: load_atoms.AtomsDataset()
   :members:
   :special-members: __getitem__, __iter__, __len__