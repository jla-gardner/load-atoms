from dataclasses import asdict

from load_atoms.database import DATASETS, DESCRIPTION_BLUEPRINT


def test_all_valid():
    for key, database_entry in DATASETS.items():
        DESCRIPTION_BLUEPRINT.validate(asdict(database_entry))
