C-GAP-20
========

Complete dataset and labels used for training both the C-GAP-20
and C-GAP-20-U models. 
For details, see here https://doi.org/10.17863/CAM.54529 
and https://doi.org/10.17863/CAM.82086


.. code-block:: python

    >>> from load_atoms import dataset
    >>> dataset("C-GAP-20")
    C-GAP-20:
        structures: 6,088
        atoms: 400,275
        species:
            C: 100.00%
        properties:
            per atom: (force_U, force)
            per structure: (energy, cutoff, nneightol, energy_U, config_type)



This dataset is licensed under the CC-BY-4.0 license.



.. code-block:: bibtex

    @article{Rowe-20-07,
        title = {An Accurate and Transferable Machine Learning Potential for Carbon},
        author = {Rowe, Patrick and Deringer, Volker L. and Gasparotto, Piero and Cs{\'a}nyi, G{\'a}bor and Michaelides, Angelos},
        year = {2020},
        journal = {The Journal of Chemical Physics},
        volume = {153},
        number = {3},
        pages = {034702},
        doi = {10.1063/5.0005084},
    }
