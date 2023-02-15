import sys
from pathlib import Path

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


def page_content(dataset_id: str) -> str:
    # avoid actually downloading the dataset
    structures = dataset(dataset_id, root=PROJECT_ROOT / "datasets")
    db_entry = DATASETS[dataset_id]

    representative_structures = db_entry.representative_structures or [*range(5)]
    representative_structures = representative_structures[: min(5, len(structures))]

    summary = str(structures)

    title = db_entry.name + "\n" + "-" * len(db_entry.name)
    visualisations = ""

    return PAGE_TEMPLATE.format(
        title=title,
        description=db_entry.description,
        dataset_id=dataset_id,
        summary=pad(summary, indent=4),
        visualisations=visualisations,
        license=db_entry.license,
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
        f.write(
            """\
Datasets
========

"""
        )
        for dataset_id in all_documented_datasets:
            f.write(f".. include:: datasets/{dataset_id}.rst\n")


if __name__ == "__main__":
    dataset_id = sys.argv[1]
    assert is_known_dataset(dataset_id), f"Dataset {dataset_id} is not known."

    build_page(dataset_id)
    build_datasets_index()
