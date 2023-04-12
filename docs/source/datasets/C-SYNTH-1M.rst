C-SYNTH-1M
==========

1 million atomic environments from a "synthetic" dataset 
created using the C-GAP-17 model to 
drive MD for 546 uncorrelated configurations. 
For details, see https://doi.org/10.1039/D2DD00137C.


.. code-block:: python

    >>> from load_atoms import dataset
    >>> dataset("C-SYNTH-1M")
    C-SYNTH-1M:
        structures: 5,460
        atoms: 1,092,000
        species:
            C: 100.00%
        properties:
            per atom: (gap17_energy, gap17_forces)
            per structure: (time, density, run_id, anneal_T)





.. code-block:: bibtex

    @article{Gardner-23-03,
      title = {Synthetic Data Enable Experiments in Atomistic Machine Learning},
      author = {Gardner, John L. A. and Beaulieu, Zo{\'e} Faure and Deringer, Volker L.},
      year = {2023},
      journal = {Digital Discovery},
      doi = {10.1039/D2DD00137C},
    }
