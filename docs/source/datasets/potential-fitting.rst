#################
Potential Fitting
#################

The following datasets were originally conceived for the purpose of fitting interatomic potentials:

.. grid:: 2

    .. grid-item-card::
        :class-item: info-card
        
        .. centered:: `C-GAP-17 <C-GAP-17.html>`_

        The complete dataset and labels used to train and test the `C-GAP-17 <https://doi.org/10.1103/PhysRevB.95.094203>`_ 
        interatomic potential for amorphous carbon.
        This dataset was built in an iterative manner, and contains 4,530 structures, covering a wide range of densities, temperatures and degrees of dis/order.
        More detail can be found in the paper's `supplementary information <https://doi.org/10.17863/CAM.7453>`_.

    .. grid-item-card::

        `C-GAP-20 <C-GAP-20.html>`_

        .. epigraph::

            This dataset probes chemical reactions of methyl halides with halide anions, i.e. 
            :math:`\text{X}^- + \text{CH}_3\text{Y} \rightarrow \text{CH}_3\text{X} +  \text{Y}^-` , and contains structures for all possible combinations of 
            :math:`\text{X},\text{Y} = \text{F}, \text{Cl}, \text{Br}, \text{I}`.

            -- Oliver T. Unke and Markus Meuwly

        See `PhysNet: A Neural Network for Predicting Energies, Forces, Dipole Moments and Partial Charges <https://doi.org/10.1021/acs.jctc.9b00181>`_ for details.
        Original files taken from `Zenodo <https://zenodo.org/records/2605341>`_, and converted to the XYZ format using
        `this script <https://github.com/jla-gardner/load-atoms/blob/main/database/SN2-19/process.py>`_.

.. toctree::
    :maxdepth: 1
    :hidden:

    C-GAP-17
    C-GAP-20
    Cu-ACE-21
    Cu-POET-19
    GST-GAP-22
    P-GAP-20
    Si-GAP-18
    SiO2-GAP-21