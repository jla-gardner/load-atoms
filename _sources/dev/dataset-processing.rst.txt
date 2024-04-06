Dataset Processing
==================

Each :class:`~load_atoms.database.DatabaseEntry` object 
defines a :class:`~load_atoms.database.processing.Chain` of steps
that sequentially transform the directory containing all of the downloaded files
for a dataset, to the list of :class:`~ase.Atoms` objects that the dataset
contains.

To specify these in the :code:`.yaml` file for a dataset, use the :code:`processing`
key using commands of the form:

.. code-block:: yaml

    processing:
      - UnZip
      - ForEachFile:
        pattern: '*.xyz'
        steps:
            - ReadASE

*i.e.,* the processing chain is a (:code:`yaml`) list of 
:class:`~load_atoms.database.processing.Step` class names,
with key-word arguments for each step specified as a dictionary.
The above example would unzip the downloaded folder, and read
all of the :code:`.xyz` files in the resulting directory.

For specific cases, (e.g. when custom formats are involved),
a custom script can be specified using the :class:`~load_atoms.database.processing.Custom`
class.

.. autoclass:: load_atoms.database.processing.Step()
    :show-inheritance:
    :members: __call__
.. autoclass:: load_atoms.database.processing.Chain
    :members: __call__
    :show-inheritance:



Available Steps
----------------

.. autoclass:: load_atoms.database.processing.UnZip
    :show-inheritance:
.. autoclass:: load_atoms.database.processing.SelectFile
    :show-inheritance:
.. autoclass:: load_atoms.database.processing.ForEachFile
    :show-inheritance:
.. autoclass:: load_atoms.database.processing.ReadASE
    :show-inheritance:
.. autoclass:: load_atoms.database.processing.Custom
    :show-inheritance: