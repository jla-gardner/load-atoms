"""
Set up the test environment by copying across the database to 
a `testing-datasets` folder and simulating a download by moving
all non-yaml files to a `temp` folder.

See this SO answer for why this __init__ structure, and corresponding
    [tool.pytest]
    norecursedirs = "tests/setup"
in `pyproject.toml` is necessary:
https://stackoverflow.com/a/46976704
"""

import shutil
from pathlib import Path

# this file is at root/tests/setup/__init__.py
PROJECT_ROOT = Path(__file__).parent.parent.parent
DATABASE_ROOT = PROJECT_ROOT / "database"
AVAILABLE_DATASETS = sorted(
    [p.stem for p in sorted(DATABASE_ROOT.glob("**/*.yaml"))]
)

# simulate downalding the datasets
TESTING_DIR = PROJECT_ROOT / "testing-datasets"
TESTING_DIR.mkdir(exist_ok=True)

for name in AVAILABLE_DATASETS:
    # copy over the folder if it doesn't exist
    shutil.copytree(
        DATABASE_ROOT / name, TESTING_DIR / name, dirs_exist_ok=True
    )
    (TESTING_DIR / name / "temp").mkdir(exist_ok=True)
    # move all non yaml files to temp to simulate a download
    for file in (TESTING_DIR / name).glob("*"):
        if (
            file.suffix != ".yaml"
            and file.name != "temp"
            and file.name != f"{name}.xyz"
        ):
            file.rename(TESTING_DIR / name / "temp" / file.name)
