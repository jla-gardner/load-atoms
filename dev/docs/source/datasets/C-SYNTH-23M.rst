C-SYNTH-23M
===========

The complete synthetic dataset from https://doi.org/10.1039/D2DD00137C.
Comprised of 546 uncorrelated MD trajectories for for 200 atoms structures
sampled every 1fs.


.. code-block:: python

    >>> from load_atoms import dataset
    >>> dataset("C-SYNTH-23M")
    C-SYNTH-23M:
        structures: 115,206
        atoms: 23,041,200
        species:
            C: 100.00%
        properties:
            per atom: (gap17_forces, gap17_energy)
            per structure: (density, anneal_T, time, run_id)





.. code-block:: bibtex

    @article{Gardner-23-03,
      title = {Synthetic Data Enable Experiments in Atomistic Machine Learning},
      author = {Gardner, John L. A. and Beaulieu, Zo{\'e} Faure and Deringer, Volker L.},
      year = {2023},
      journal = {Digital Discovery},
      doi = {10.1039/D2DD00137C},
    }
