Si-GAP-18
=========

Complete dataset for training Si-GAP-18 model. 
For details, see the supplementary information here:
https://doi.org/10.5281/zenodo.1250555


.. code-block:: python

    >>> from load_atoms import dataset
    >>> dataset("Si-GAP-18")
    Si-GAP-18:
        structures: 2,475
        atoms: 171,815
        species:
            Si: 100.00%
        properties:
            per atom: (force)
            per structure: (energy, nneightol, cutoff, config_type)



This dataset is licensed under the CC BY-NC-SA 4.0 license.



.. code-block:: bibtex

    @article{Bartok-18-12,
        title = {Machine {{Learning}} a {{General-Purpose Interatomic Potential}} for {{Silicon}}},
        author = {Bart{\'o}k, Albert P. and Kermode, James and Bernstein, Noam and Cs{\'a}nyi, G{\'a}bor},
        year = {2018},
        month = dec,
        journal = {Physical Review X},
        volume = {8},
        number = {4},
        pages = {041048},
    }
