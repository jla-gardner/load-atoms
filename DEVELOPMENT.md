# How to develop `load-atoms` locally

## 1. Clone the repo

```bash
git clone https://github.com/jla-gardner/load-atoms
cd load-atoms
```

## 2. Install dependencies

It is highly recommended that you use a virtual environment to develop this project.
Using `conda`, you can do:

```bash
conda create -n load-atoms python=3.8 -y
conda activate load-atoms
```

Once you've created a virtual environment, you can `pip install` this package, together with the necessary development tools, in a local and editable mode using:

```bash
pip install -e ".[dev]"
```

This project uses the `black` code formatter, together with `isort` to sort imports.
For this reason, it is highly recommended that you set up your editor to run `black` and `isort` on save. If using VSCode, installing the `isort` extension, together with the included `.vscode/settings.json` file, is enough to make this happen automatically.

## 3. Test your installation

To test your installation, run:

```bash
pytest
```
