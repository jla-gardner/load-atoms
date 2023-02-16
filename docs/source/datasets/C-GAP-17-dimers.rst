C-GAP-17-dimers
===============

Carbon dimers with bond lengths ascending from 0.8Å to 3.7Å in incremenets of 0.1Å. Labelled with DFT as taken from the supplementary information of Deringer and Csányi (2017).


.. code-block:: python

    >>> from load_atoms import dataset
    >>> dataset("C-GAP-17-dimers")
    C-GAP-17-dimers:
        counts:
            structures: 30
            atoms: 60
        species:
            C: 100.00%
        properties:
            per atom: (force)
            per structure: (energy, detailed_ct, config_type)



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
