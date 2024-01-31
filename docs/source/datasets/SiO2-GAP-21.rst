SiO2-GAP-21
===========

The training database Erhard et al. used to fit their GAP-21 potential for silica. 
More details available at https://doi.org/10.1038/s41524-022-00768-w


.. code-block:: python

    >>> from load_atoms import dataset
    >>> dataset("SiO2-GAP-21")
    SiO2-GAP-21:
        structures: 3,074
        atoms: 268,118
        species:
            O: 66.47%
            Si: 33.53%
        properties:
            per atom: (forces)
            per structure: (free_energy, energy, virials, config_type)



This dataset is licensed under the CC-BY-4.0 license.



.. code-block:: bibtex

    @article{Erhard-22-04,
      title = {A Machine-Learned Interatomic Potential for Silica and Its Relation to Empirical Models},
      author = {Erhard, Linus C. and Rohrer, Jochen and Albe, Karsten and Deringer, Volker L.},
      year = {2022},
      journal = {npj Computational Materials},
      volume = {8},
      number = {1},
      pages = {1--12},
    }
