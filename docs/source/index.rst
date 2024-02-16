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
   >>> dataset = load_dataset("C-GAP-17")
   Downloading C-GAP-17.extxyz | ███████████████████████ | 100.0% 
   The C-GAP-17 dataset is covered by the CC BY-NC-SA 4.0 license.
   Please cite the C-GAP-17 dataset if you use it in your work.

The resulting :class:`~load_atoms.AtomsDataset` wraps 
a list of :class:`ase.Atoms <ase.atoms.Atoms>`:

.. code-block:: pycon

   >>> dataset[0] # treat the dataset like a list of ase.Atoms
   Atoms(symbols='C64', pbc=True, cell=[9.483, 9.483, 9.483], force=...)

... and provides useful dataset-level methods and properties:

.. code-block:: pycon

   >>> dataset.info["energy"]  
   array([-9847.661671, -9886.440245, -9916.681692, ...,  -632.464825,
           -632.146922,  -632.944571])
   >>> dataset.structure_sizes  
   array([64, 64, 64, ...,  4,  4,  4])
   >>> train, val, test = dataset.random_split([0.8, 0.1, 0.1], seed=42)

For a full list of such methods, see the :class:`~load_atoms.AtomsDataset` documentation. 
:code:`load-atoms` also contains a :func:`~load_atoms.view` function to interactivley 
visualize atomic structures directly in a notebook: 


.. code-block:: pycon

   >>> from load_atoms import view
   >>> view(dataset[1926], show_bonds=True)  

.. raw:: html
   :file: ./_static/c-gap-17-1926.html

         
Installation
------------
.. _installation:

.. code-block:: console

   $ pip install load-atoms


.. toctree::
   :maxdepth: 3
   :hidden:
   :caption: API Reference

   api/dataset
   api/database
   api/viz
   api/utils

.. include:: datasets-index.rst


Development & Contributions
---------------------------
We welcome any suggestions and contributions to this project.
Please visit our `GitHub repository <https://github.com/jla-gardner/load-atoms>`_ to report issues or submit pull requests.
The `developer guide <https://github.com/jla-gardner/load-atoms/blob/main/dev/developer-guide>`_ contains information on how to set up a development environment and run the tests.


