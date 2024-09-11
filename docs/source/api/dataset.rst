Dataset
=======

The main entry point of :code:`load-atoms` is the :func:`load_dataset <load_atoms.load_dataset>` function:

.. autofunction:: load_atoms.load_dataset
.. autoclass:: load_atoms.AtomsDataset()
   :members:
   :special-members: __getitem__, __iter__, __len__
.. autoclass:: load_atoms.atoms_dataset.InMemoryAtomsDataset()
.. autoclass:: load_atoms.atoms_dataset.LmdbAtomsDataset()