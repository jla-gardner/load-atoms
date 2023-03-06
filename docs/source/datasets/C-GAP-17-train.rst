C-GAP-17-train
==============

Complete training dataset for the C-GAP-17 model. 
For details, see the supplementary information here:
https://www.repository.cam.ac.uk/handle/1810/262814


.. code-block:: python

    >>> from load_atoms import dataset
    >>> dataset("C-GAP-17-train")
    C-GAP-17-train:
        structures: 4,080
        atoms: 256,628
        species:
            C: 100.00%
        properties:
            per atom: (force)
            per structure: (detailed_ct, energy, config_type)

A representative structure from this dataset:

.. raw:: html
    :file: ../_static/visualisations/x3d.html

.. raw:: html
   :file: ../_static/visualisations/C-GAP-17-train/1.html



This dataset is licensed under the CC BY-NC-SA 4.0 license.



.. code-block:: bibtex

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
