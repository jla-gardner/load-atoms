Load Atoms
==========

.. warning::

   This project is under active development. Until version 1.0.0 is released, breaking changes to the API may occur.

**L**\arge **O**\pen **A**\ccess **D**\atasets for **Ato**\mistic **M**\aterials **S**\cience

Use this python package to easily access datasets of atomic structures.

Installation
------------
.. _installation:

.. code-block:: console

   $ pip install load-atoms

Usage
-----

The main entry point to `load-atoms` is the :func:`dataset` function. This can be used to download any dataset that this package currently supports:

.. code-block:: python

   >>> from load_atoms import dataset
   >>> structures = dataset("C-GAP-17")
   Downloading C-GAP-17.extxyz
   100.0% | ██████████████████████████████████████████████████

   This dataset is covered by the CC BY-NC-SA 4.0 license.
   Please cite this dataset if you use it in your work.
   For more information about this dataset, see here:
   https://jla-gardner.github.io/load-atoms/datasets/C-GAP-17.html
   
:code:`structures` is a :class:`Dataset` object. This is a lightweight wrapper around a list of :class:`ase.Atoms` objects, and can be used as such:

.. code-block:: python

      >>> structures
      C-GAP-17:
         structures: 4,530
         atoms: 284,965
         species:
            C: 100.00%
         properties:
            per atom: (force)
            per structure: (config_type, detailed_ct, split, energy)
      >>> len(structures)
      4080
      >>> structures[0]
      Atoms(symbols='C64', pbc=True, cell=[9.483921, 9.483921, 9.483921], force=...)


.. toctree::
   :maxdepth: 1
   :hidden:
 
   Home <self>

.. toctree::
   :maxdepth: 3
   :caption: API:
   :hidden:

   api

.. toctree::
   :maxdepth: 3
   :caption: Example Usage:
   :hidden:

   examples/basics.ipynb

.. include:: datasets.rst

Development & Contributions
---------------------------
We welcome any suggestions and contributions to this project.
Please visit our `GitHub repository <https://github.com/jla-gardner/load-atoms>`_ to report issues or submit pull requests.
The `developer guide <https://github.com/jla-gardner/load-atoms/blob/main/dev/developer-guide>`_ contains information on how to set up a development environment and run the tests.
