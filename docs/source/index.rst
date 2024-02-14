hidden
======

.. raw:: html
    :file: hide-title.html

.. image:: logo.svg
   :align: center
   :alt: load-atoms logo
   :width: 400px
   :target: .


.. important::

   This project is under active development. Until version 1.0.0 is released, breaking changes to the API may occur.

Usage
-----

Use :func:`load_dataset() <load_atoms.load_dataset>` to easily download, inspect and manipulate datasets of atomic structures. The complete collection of (currently available) datasets is available `here <datasets/AC-2D-22.html>`_ .

.. code-block:: pycon

   >>> from load_atoms import load_dataset
   >>> dataset = load_dataset("QM7")
   Downloading QM7.extxyz | ███████████████████████ | 100.0% 
   Please cite the QM7 dataset if you use it in your work.

The resulting :class:`AtomsDataset <load_atoms.dataset.AtomsDataset>` wraps 
a list of :class:`ase.Atoms <ase.atoms.Atoms>`:

.. code-block:: pycon

   >>> dataset[0] # treat the dataset like a list of ase.Atoms
   Atoms(symbols='CH4', pbc=False) 

... and provides useful dataset-level methods and properties:

.. code-block:: pycon

   >>> dataset.info["energy"]  # access per-structure properties via .info
   array([-18.1366, -30.9142, -24.4829, ..., -72.1238, -77.327 , -83.2715])
   >>> dataset.structure_sizes  # get the number of atoms in each structure
   array([ 5,  8,  6, ..., 16, 17, 19])

For a full list of such methods, see the :class:`AtomsDataset <load_atoms.dataset.AtomsDataset>` documentation.

.. code-block:: pycon

   >>> from load_atoms import view
   >>> # visualize a structure in the dataset
   >>> view(dataset[6492], show_bonds=True)  

.. raw:: html
   :file: ./_static/qm7-6492.html

         
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


