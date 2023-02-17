import shutil
import sys
from pathlib import Path

from x3d import visualisation_for

from load_atoms import dataset
from load_atoms.database import DATASETS, is_known_dataset

THIS_FILE = Path(__file__).resolve()
PROJECT_ROOT = THIS_FILE.parent.parent
DOC_SOURCE = PROJECT_ROOT / "docs/source"


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
    # avoid actually downloading the dataset
    structures = dataset(dataset_id, root=PROJECT_ROOT / "datasets")
    db_entry = DATASETS[dataset_id]
    summary = str(structures)

    license = ""
    if db_entry.license:
        license = LICENSE.format(license=db_entry.license)

    title = db_entry.name + "\n" + "=" * len(db_entry.name)

    visualisations = ""
    if db_entry.representative_structures:
        shutil.rmtree(DOC_SOURCE / "_static/visualisations" / dataset_id)
        visualisations += VISUALISATION
        for i in db_entry.representative_structures[:1]:
            # TODO work out how to show more than 1 visualisation without
            # them breaking onto new lines
            structures[i].wrap()
            x3d = visualisation_for(structures[i])
            ref = f"_static/visualisations/{dataset_id}/{i}.html"
            fname = DOC_SOURCE / ref
            fname.parent.mkdir(parents=True, exist_ok=True)
            with open(fname, "w") as f:
                f.write(x3d)
            visualisations += f".. raw:: html\n   :file: ../{ref}\n\n"

    return PAGE_TEMPLATE.format(
        title=title,
        description=dataset.description,
        dataset_id=dataset_id,
        summary=pad(summary, indent=4),
        visualisations=visualisations,
        license=license,
        citation=pad(db_entry.citation, indent=4),
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

    with open(DOC_SOURCE / "datasets.rst", "w") as f:
        for dataset_id in all_documented_datasets:
            f.write(f".. include:: datasets/{dataset_id}.rst\n")


if __name__ == "__main__":
    dataset_id = sys.argv[1]
    assert is_known_dataset(dataset_id), f"Dataset {dataset_id} is not known."

    build_page(dataset_id)
    build_datasets_index()
