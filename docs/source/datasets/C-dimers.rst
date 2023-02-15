C-dimers
--------

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
            per structure: (mix_history_length, smearing_width, task, mixing_scheme, pdos_calculate_weights,
                opt_strategy, spin_polarized, fix_occupancy, detailed_ct, finite_basis_corr,
                nneightol, cutoff, elec_energy_tol, max_scf_cycles, mix_charge_amp, castep_file_name,
                write_checkpoint, calculate_stress, nextra_bands, xc_functional, popn_calculate,
                cut_off_energy, virNOTUSED, config_type, kpoints_mp_grid, castep_run_time,
                energy)



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
