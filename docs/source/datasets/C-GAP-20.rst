C-GAP-20
========

Complete dataset and labels used for training both the C-GAP-20
and C-GAP-20-U models. 
For details, see the supplementary information here:
https://www.repository.cam.ac.uk/handle/1810/307452
and here:
https://www.repository.cam.ac.uk/handle/1810/336687


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
            per structure: (energy_U, energy, config_type)

A representative structure from this dataset:

.. raw:: html
    :file: ../_static/visualisations/x3d.html

.. raw:: html
   :file: ../_static/visualisations/C-GAP-20/1.html



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
