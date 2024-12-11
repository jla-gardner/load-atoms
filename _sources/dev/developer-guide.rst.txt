Development
===========

We welcome any suggestions and contributions to this project.
Please visit our `GitHub repository <https://github.com/jla-gardner/load-atoms>`_ to report issues or submit pull requests.

Setup
-----

1. Clone the repo
++++++++++++++++++

.. code-block:: bash

    git clone https://github.com/jla-gardner/load-atoms
    cd load-atoms

2. Install dependencies.
+++++++++++++++++++++++++
It is highly recommended that you use a virtual environment to develop this project.
Using :code:`conda`, you can do:

.. code-block:: bash

    conda create -n load-atoms python=3.10 -y
    conda activate load-atoms

Once you've created a virtual environment, you can :code:`pip install` this package, together with the necessary development tools, in a local and editable mode using:

.. code-block:: bash

    pip install -e ".[dev]"

This project uses the :code:`ruff` code formatter. If you are using VSCode, installing the ruff extension, and adding 
the following to your :code:`.vscode/settings.json` file will enable automatic formatting on save:

.. code-block:: 

    {
        ...
        "[python]": {
            "editor.codeActionsOnSave": {
                "source.organizeImports": "explicit"
            },
            "editor.formatOnSave": true,
            "editor.defaultFormatter": "charliermarsh.ruff"
        },
        ...
    }


3. Test your installation.
++++++++++++++++++++++++++


.. code-block:: bash

    pytest


Codebase
--------

For an ad-hoc guide to the internal (i.e. non-user-facing) codebase, see:

.. toctree::
   :maxdepth: 2

   dataset-loading
   building-the-docs