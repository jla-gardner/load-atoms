C-GAP-17-train
--------------

Complete training dataset for the C-GAP-17 model. For details, see the supplementary information here: https://www.repository.cam.ac.uk/handle/1810/262814


.. code-block:: python

    >>> from load_atoms import dataset
    >>> dataset("C-GAP-17-train")
    C-GAP-17-train:
        counts:
            structures: 4,080
            atoms: 256,628
        species:
            C: 100.00%
        properties:
            per atom: (frac_pos, force)
            per structure: (mix_history_length, smearing_width, task, mixing_scheme, pdos_calculate_weights,
                opt_strategy, spin_polarized, fix_occupancy, finite_basis_corr, detailed_ct,
                nneightol, cutoff, elec_energy_tol, max_scf_cycles, castep_file_name,
                write_checkpoint, calculate_stress, nextra_bands, xc_functional, energy,
                popn_calculate, cut_off_energy, config_type, kpoints_mp_grid, castep_run_time,
                mix_charge_amp)



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
