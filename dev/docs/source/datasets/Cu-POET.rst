Cu-POET
=======

Cu dataset, with DFT labels, originally used for training symbolic
interatomic potentials, using the POET framework (https://gitlab.com/muellergroup/poet).
Also included are a selection of low index surfaces for testing.


.. code-block:: python

    >>> from load_atoms import dataset
    >>> dataset("Cu-POET")
    Cu-POET:
        structures: 163
        atoms: 5,051
        species:
            Cu: 100.00%
        properties:
            per atom: (forces)
            per structure: (energy, config_type, stress)





.. code-block:: bibtex

    @article{Hernandez-19-11,
        title = {Fast, Accurate, and Transferable Many-Body Interatomic Potentials by Symbolic Regression},
        author = {Hernandez, Alberto and Balasubramanian, Adarsh and Yuan, Fenglin and Mason, Simon A. M. and Mueller, Tim},
        year = {2019},
        journal = {npj Computational Materials},
        volume = {5},
        number = {1},
        pages = {1--11},
        doi = {10.1038/s41524-019-0249-1},
    }
