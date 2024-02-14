from __future__ import annotations

import shutil
from pathlib import Path
from typing import Callable

from load_atoms import load_dataset, view
from load_atoms.dataset import DescribedDataset
from load_atoms.dataset_info import valid_licenses

# this file is at dev/scripts/pages.py
_PROJECT_ROOT = Path(__file__).parent.parent.parent
_DOC_SOURCE = _PROJECT_ROOT / "docs/source"
_DOWNLOAD_DIR = _PROJECT_ROOT / "testing-datasets"


def build_docs_page_for(name: str):
    # avoid downloading the dataset so that if local changes have been made,
    # they are reflected in the documentation preview
    shutil.copytree(
        _PROJECT_ROOT / "database" / name,
        _DOWNLOAD_DIR / name,
        dirs_exist_ok=True,
    )
    dataset = load_dataset(name, root=_DOWNLOAD_DIR)

    raw_rst = "\n\n".join(func(dataset) for func in _page_component_generators)  # type: ignore
    with open(_DOC_SOURCE / "datasets" / f"{name}.rst", "w") as f:
        f.write(raw_rst)


def build_datasets_index():
    all_documented_datasets = (_DOC_SOURCE / "datasets").glob("*.rst")
    all_documented_datasets = sorted([p.stem for p in all_documented_datasets])
    contents = """\
.. This file is autogenerated by dev/scripts/generate_page.py

.. toctree::
    :maxdepth: 3
    :caption: Available Datasets:
    :hidden:
    
"""
    for dataset_id in all_documented_datasets:
        contents += f"    datasets/{dataset_id}\n"

    with open(_DOC_SOURCE / "datasets.rst", "w") as f:
        f.write(contents)


ComponentGenerator = Callable[[DescribedDataset], str]
_page_component_generators: list[ComponentGenerator] = []


def register_component(func: ComponentGenerator):
    _page_component_generators.append(func)
    return func


@register_component
def auto_generated_warning(dataset: DescribedDataset) -> str:
    return ".. This file is autogenerated by dev/scripts/generate_page.py"


@register_component
def title(dataset: DescribedDataset) -> str:
    name = dataset.description.name
    return name + "\n" + "=" * len(name)


@register_component
def header(dataset: DescribedDataset) -> str:
    idx: int = dataset.description.representative_structure  # type: ignore
    if idx is None:
        # get first structure with more than 1 atom
        for i, s in enumerate(dataset):
            if len(s) > 1:
                idx = i
                break

    html_visualisation = view(dataset[idx], show_bonds=True)
    viz = '<div class="viz">' + html_visualisation.data + "</div>"

    file_name = f"_static/visualisations/{dataset.description.name}.html"
    (_DOC_SOURCE / "_static/visualisations").mkdir(exist_ok=True)
    with open(_DOC_SOURCE / file_name, "w") as f:
        f.write(viz)

    info = str(dataset.description.description).replace("\n", "\n        ")
    return f"""\
.. grid:: 2
    
    .. grid-item::

        .. raw:: html
            :file: ../{file_name}

    .. grid-item::
        :class: info-card

        {info}
"""


@register_component
def code_block(dataset: DescribedDataset) -> str:
    summary = str(dataset).replace("\n", "\n    ")
    return f"""\
.. code-block:: python

    >>> from load_atoms import load_dataset
    >>> load_dataset("{dataset.description.name}")
    {summary}
"""


@register_component
def license(dataset: DescribedDataset) -> str:
    if dataset.description.license is None:
        return ""

    license = dataset.description.license
    url = valid_licenses[license]
    return f"""\
License
-------

This dataset is licensed under the `{license} <{url}>`_ license.
"""


@register_component
def citation(dataset: DescribedDataset) -> str:
    if dataset.description.citation is None:
        return ""

    citation = dataset.description.citation.replace("\n", "\n    ")
    return f"""\
Citation
--------

If you use this dataset in your work, please cite the following:

.. code-block:: latex
    
    {citation}
"""
