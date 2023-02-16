C-dimers
========

Carbon dimers with bond lengths ascending from 0.8Å to 3.7Å in incremenets of 0.1Å. Labelled with DFT as taken from the supplementary information of Deringer and Csányi (2017).


.. code-block:: python

    >>> from load_atoms import dataset
    >>> dataset("C-dimers")
    C-dimers:
        counts:
            structures: 30
            atoms: 60
        species:
            C: 100.00%
        properties:
            per atom: (frac_pos, force)
            per structure: (max_scf_cycles, finite_basis_corr, xc_functional, castep_run_time,
                elec_energy_tol, detailed_ct, popn_calculate, cut_off_energy, opt_strategy,
                cutoff, task, write_checkpoint, smearing_width, pdos_calculate_weights,
                energy, config_type, nextra_bands, fix_occupancy, spin_polarized, castep_file_name,
                mix_charge_amp, calculate_stress, mix_history_length, mixing_scheme, kpoints_mp_grid,
                virNOTUSED, nneightol)



https://creativecommons.org/licenses/by-nc-sa/4.0/

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
