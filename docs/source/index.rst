
.. important::

   This project is under active development. Until version 1.0.0 is released, breaking changes to the API may occur.

:code:`load-atoms` Documentation
================================

Use :func:`load_atoms.dataset` to easily download, access and manipulate datasets of atomic structures:

.. code-block:: pycon

   >>> from load_atoms import dataset
   >>> structures = dataset("QM7")
   Downloading QM7.extxyz | ███████████████████████ | 100.0% 
   Please cite this dataset if you use it in your work.

The resulting :class:`AtomsDataset <load_atoms.dataset.AtomsDataset>` wraps 
a list of :class:`ase.Atoms <ase.atoms.Atoms>`, and provides useful methods to access these:

.. code-block:: pycon

   >>> structures[0] # treat the dataset like a list of ase.Atoms
   Atoms(symbols='CH4', pbc=False) 
   >>> structures.info["energy"]  # access per-structure properties
   array([-18.1366, -30.9142, -24.4829, ..., -72.1238, -77.327 , -83.2715])
   >>> print(structures) # print a summary of the dataset
   QM7:
    structures: 7,165
    atoms: 110,650
    species:
        H: 56.00%
        C: 32.32%
        N: 6.01%
        O: 5.40%
        S: 0.27%
    properties:
        per atom: ()
        per structure: (energy)

For a full list of available methods, see the :class:`AtomsDataset <load_atoms.dataset.AtomsDataset>` documentation.
For a full list of datasets that can be downloaded, see the :ref:`datasets` section.
Have you own, locally stored dataset? You can make full use of the :class:`AtomsDataset <load_atoms.dataset.AtomsDataset>` class by simply passing the path to your dataset to :func:`load_atoms.dataset`:

.. code-block:: pycon

   >>> structures = dataset("path/to/structures.xyz")


         
Installation
------------
.. _installation:

.. code-block:: console

   $ pip install load-atoms


.. toctree::
   :maxdepth: 3
   :hidden:

   api

.. toctree::
   :maxdepth: 3
   :hidden:

   examples

.. include:: datasets.rst

Development & Contributions
---------------------------
We welcome any suggestions and contributions to this project.
Please visit our `GitHub repository <https://github.com/jla-gardner/load-atoms>`_ to report issues or submit pull requests.
The `developer guide <https://github.com/jla-gardner/load-atoms/blob/main/dev/developer-guide>`_ contains information on how to set up a development environment and run the tests.


.. image:: logo.svg
   :align: center
   :alt: load-atoms logo
   :width: 400px