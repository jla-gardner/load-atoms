.. load-atoms documentation master file, created by
   sphinx-quickstart on Wed Feb 15 20:27:06 2023.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

⚛️ load-atoms 🧪
=================


.. warning::

   This project is under active development. Until version 1.0.0 is released, breaking changes to the API may occur.

**L**\arge **O**\pen **A**\ccess **D**\atasets for **Ato**\mistic **M**\aterials **S**\cience

Use this python package to easily access datasets of atomic structures.

Installation
------------
.. _installation:

.. code-block:: console

   (.venv) $ pip install load-atoms

Usage
-----

The main entry point to `load-atoms` is the :func:`dataset` function. This can be used to download any dataset that this package currently :ref:`currently supports. <datasets>` 

.. code-block:: python

      >>> from load_atoms import dataset
      >>> structures = dataset("C-GAP-17-train")

      Downloading C-GAP-17.extxyz from https://github.com/jla-gardner/load-atoms/
      100.0% | ███████████████████████████████████████

      Complete training dataset for the C-GAP-17 model. 
      For details, see the supplementary information here: 
      https://www.repository.cam.ac.uk/handle/1810/262814
      This dataset is licensed under https://creativecommons.org/licenses/by-nc-sa/4.0/
      If you use this dataset, please cite the following:
      @article{Deringer-17,
         title = {Machine learning based interatomic potential for amorphous carbon},
         doi = {10.1103/PhysRevB.95.094203},
         volume = {95},
         number = {9},
         urldate = {2021-07-15},
         journal = {Physical Review B},
         author = {Deringer, Volker L. and Cs{\'a}nyi, G{\'a}bor},    
         year = {2017},
         pages = {094203},
      }

:code:`structures` is a :class:`Dataset` object. This is a lightweight wrapper around a list of :class:`ase.Atoms` objects, and can be used as such:

.. code-block:: python

      >>> len(structures)
      4080
      >>> structures[0]
      Atoms(symbols='C64', pbc=True, cell=[9.483921, 9.483921, 9.483921], force=...)




Overview
--------

.. toctree::
   :maxdepth: 1

   Home <self>

.. toctree::
   :maxdepth: 3
   :caption: API Reference:

   api

.. toctree::
   :maxdepth: 3
   :caption: Datasets:

   datasets