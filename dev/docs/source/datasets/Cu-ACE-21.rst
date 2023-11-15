Cu-ACE-21
=========

Cu dataset originally used for training ACE potentials. Labelled with 
DFT using the PBE functional.


.. code-block:: python

    >>> from load_atoms import dataset
    >>> dataset("Cu-ACE-21")
    Cu-ACE-21:
        structures: 1,000
        atoms: 11,309
        species:
            Cu: 100.00%
        properties:
            per atom: (forces)
            per structure: (name, energy)





.. code-block:: bibtex

    @article{Lysogorskiy-21-06,
        title = {Performant Implementation of the Atomic Cluster Expansion ({{PACE}}) and Application to Copper and Silicon},
        author = {Lysogorskiy, Yury and van der Oord, Cas and Bochkarev, Anton and Menon, Sarath and Rinaldi, Matteo and Hammerschmidt, Thomas and Mrovec, Matous and Thompson, Aidan and Cs{\'a}nyi, G{\'a}bor and Ortner, Christoph and Drautz, Ralf},
        year = {2021},
        journal = {npj Computational Materials},
        volume = {7},
        number = {1},
        pages = {1--12},
        doi = {10.1038/s41524-021-00559-9},
    }
