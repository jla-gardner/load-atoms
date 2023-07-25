QM7
===

a collection of saturated, small molecules containing up to 7 heavy atoms
with geometries relaxed using an empirical potential


.. code-block:: python

    >>> from load_atoms import dataset
    >>> dataset("QM7")
    QM7:
        structures: 7,165
        atoms: 110,650
        species:
            H: 56.00%
            C: 32.32%
            N: 6.01%
            O: 5.40%
            S: 0.27%
        properties:
            per atom: ()
            per structure: (energy)

A representative structure from this dataset:

.. raw:: html
    :file: ../_static/visualisations/x3d.html

.. raw:: html
   :file: ../_static/visualisations/QM7/1.html





.. code-block:: bibtex

    @inproceedings{Montavon-12,
        author = {Montavon, Gr\'{e}goire and Hansen, Katja and Fazli, Siamac and Rupp, Matthias and Biegler, Franziska and Ziehe, Andreas and Tkatchenko, Alexandre and Lilienfeld, Anatole and M\"{u}ller, Klaus-Robert},
        booktitle = {Advances in Neural Information Processing Systems},
        editor = {F. Pereira and C.J. Burges and L. Bottou and K.Q. Weinberger},
        title = {Learning Invariant Representations of Molecules for Atomization Energy Prediction},
        volume = {25},
        year = {2012}
    }
    @article{Rupp-12,
        title = {Fast and Accurate Modeling of {Molecular Atomization Energies with Machine Learning},
        author = {Rupp, Matthias and Tkatchenko, Alexandre and M{\"u}ller, Klaus-Robert and {von Lilienfeld}, O. Anatole},
        year = {2012},
        journal = {Physical Review Letters},
        volume = {108},
        number = {5},
        pages = {058301},
        doi = {10.1103/PhysRevLett.108.058301}
    }
