import shutil
import sys
from pathlib import Path

from load_atoms import dataset
from load_atoms.dataset import DescribedDataset
from load_atoms.dataset_info import DatasetInfo

# this file is at dev/scripts/rebuild_all_docs.py
PROJECT_ROOT = Path(__file__).parent.parent.parent
# database is at root/database/
DATASETS = [d.name for d in (PROJECT_ROOT / "database").glob("*") if d.is_dir()]
# docs are at docs/
DOC_SOURCE = PROJECT_ROOT / "docs/source"
# source folder for dataset downloads
DOWNLOAD_DIR = PROJECT_ROOT / "testing-datasets"

PAGE_TEMPLATE = """\
{title}

{description}

.. code-block:: python

    >>> from load_atoms import dataset
    >>> dataset("{dataset_id}")
{summary}

{visualisations}

{license}

.. code-block:: bibtex

{citation}
"""

VISUALISATION = """\
A representative structure from this dataset:

.. raw:: html
    :file: ../_static/visualisations/x3d.html

"""

LICENSE = """\
This dataset is licensed under the {license} license.

"""


def page_content(dataset_id: str) -> str:
    # delete the dataset if it exists
    shutil.rmtree(DOWNLOAD_DIR / dataset_id, ignore_errors=True)

    # copy over what we need
    shutil.copytree(
        PROJECT_ROOT / "database" / dataset_id,
        DOWNLOAD_DIR / dataset_id,
    )

    # avoid actually downloading the dataset
    structures: DescribedDataset = dataset(dataset_id, root=DOWNLOAD_DIR)  # type: ignore
    dataset_description: DatasetInfo = structures.description

    summary = str(structures)

    license = ""
    if dataset_description.license:
        license = LICENSE.format(license=dataset_description.license)

    title = (
        dataset_description.name + "\n" + "=" * len(dataset_description.name)
    )

    visualisations = ""
    # TODO un break this
    # if dataset_description.representative_structures:
    #     shutil.rmtree(
    #         DOC_SOURCE / "_static/visualisations" / dataset_id, ignore_errors=True
    #     )
    #     visualisations += VISUALISATION
    #     for i in dataset_description.representative_structures[:1]:
    #         # TODO work out how to show more than 1 visualisation without
    #         # them breaking onto new lines
    #         structures[i].wrap()
    #         structures[i].center()
    #         x3d = visualisation_for(structures[i])
    #         ref = f"_static/visualisations/{dataset_id}/{i}.html"
    #         fname = DOC_SOURCE / ref
    #         fname.parent.mkdir(parents=True, exist_ok=True)
    #         with open(fname, "w") as f:
    #             f.write(x3d)
    #         visualisations += f".. raw:: html\n   :file: ../{ref}\n\n"

    citation = dataset_description.citation or ""
    return PAGE_TEMPLATE.format(
        title=title,
        description=dataset_description.description,
        dataset_id=dataset_id,
        summary=pad(summary, indent=4),
        visualisations=visualisations,
        license=license,
        citation=pad(citation, indent=4),
    )


def pad(s: str, indent: int = 4) -> str:
    _pad = " " * indent
    return "\n".join(_pad + line for line in s.splitlines())


def build_page(dataset_id):
    content = page_content(dataset_id)

    with open(DOC_SOURCE / "datasets" / f"{dataset_id}.rst", "w") as f:
        f.write(content)


def build_datasets_index():
    all_documented_datasets = (DOC_SOURCE / "datasets").glob("*.rst")
    all_documented_datasets = sorted([p.stem for p in all_documented_datasets])
    contents = """\
.. toctree::
    :maxdepth: 3
    :caption: Datasets:
    :hidden:
    
"""
    for dataset_id in all_documented_datasets:
        contents += f"    datasets/{dataset_id}\n"

    with open(DOC_SOURCE / "datasets.rst", "w") as f:
        f.write(contents)


if __name__ == "__main__":
    dataset_id = sys.argv[1]

    build_page(dataset_id)
    build_datasets_index()
