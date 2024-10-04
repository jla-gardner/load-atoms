Configuration
=============


``load-atoms`` has several behaviours that can be configured using environment variables.

.. envvar:: LOAD_ATOMS_VERBOSE

   Controls the verbosity of the ``load-atoms`` package.

   If set to 1, ``load-atoms`` will print information about the dataset being loaded. (Default)

   If set to 0, ``load-atoms`` will not print any information about the dataset being loaded.


.. envvar:: LOAD_ATOMS_DEBUG

   If set to 1, ``load-atoms`` will not delete any auxiliary files created during the loading process.

   If set to 0, ``load-atoms`` will delete all auxiliary files created during the loading process. (Default)

