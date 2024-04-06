load-atoms
==========

.. raw:: html
    :file: hide-title.html

.. image:: logo.svg
   :align: center
   :alt: load-atoms logo
   :width: 400px
   :target: .


.. important::

   This project is under active development. Until version 1.0.0 is released, breaking changes to the API may occur.

:code:`load-atoms` is a Python package for downloading, inspecting and manipulating datasets of atomic structures.

Quickstart
----------
Install using :code:`pip install load-atoms`, and then use 
:func:`~load_atoms.load_dataset` to download an :class:`~load_atoms.AtomsDataset` (full list available :doc:`here <database-summary>`):

   >>> from load_atoms import load_dataset
   >>> dataset = load_dataset("QM9")
   ╭───────────────────────────────── QM9 ─────────────────────────────────╮
   │                                                                       │
   │   Downloading dsgdb9nsd.xyz.tar.bz2 ━━━━━━━━━━━━━━━━━━━━ 100% 00:09   │
   │   Extracting dsgdb9nsd.xyz.tar.bz2  ━━━━━━━━━━━━━━━━━━━━ 100% 00:18   │
   │   Processing files                  ━━━━━━━━━━━━━━━━━━━━ 100% 00:19   │
   │   Caching to disk                   ━━━━━━━━━━━━━━━━━━━━ 100% 00:02   │
   │                                                                       │
   │            The QM9 dataset is covered by the CC0 license.             │
   │        Please cite the QM9 dataset if you use it in your work.        │
   │          For more information about the QM9 dataset, visit:           │
   │                            load-atoms/QM9                             │
   ╰───────────────────────────────────────────────────────────────────────╯
   
These are thin wrappers around lists of :class:`ase.Atoms`:

   >>> dataset[0]
   Atoms(symbols='CH4', pbc=False, partial_charges=...)

:func:`~load_atoms.view` provides interactive visualization of atomic structures:

   >>> from load_atoms import view
   >>> view(dataset[23_810], show_bonds=True)

.. raw:: html
   :file: ./_static/qm9-22031.html

We provide several :doc:`dataset-level operations <api/dataset>`:

   >>> small_structures = dataset.filter_by(lambda atoms: len(atoms) < 10)

   >>> dataset.info["energy"]
   array([-10.5498, -6.9933,  ...,  -5.7742, -6.3021])

   >>> trainset, testset = dataset.random_split([0.9, 0.1], seed=42)


Contributing
------------

`load-atoms <.>`_ was originally conceived and developed by me, `John Gardner <https://jla-gardner.github.io>`_, 
as part of my PhD research at the University of Oxford within the `Deringer Group <https://www.chem.ox.ac.uk/people/volker-deringer>`_.

If you are interested in contributing to the project, be that adding new functionality, 
suggesting a dataset or fixing a bug, please see the :doc:`developer guide <dev/developer-guide>` and feel free to open an issue or pull request on the `GitHub repository <https://github.com/jla-gardner/load-atoms>`_.

.. toctree::
   :maxdepth: 1
   :hidden:

   Quickstart <self>


.. toctree::
   :maxdepth: 3
   :hidden:
   :caption: API Reference

   api/dataset
   api/viz
   api/utils

.. include:: datasets-index.rst


.. toctree::
   :maxdepth: 1
   :hidden:
   :caption: Contributing

   dev/developer-guide

