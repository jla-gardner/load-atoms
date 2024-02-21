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
    (TESTING_DIR / name).mkdir(exist_ok=True)
    shutil.copy(
        DATABASE_ROOT / name / f"{name}.yaml",
        TESTING_DIR / name / f"{name}.yaml",
    )
    # simulate download by moving any non-yaml files to the temp folder
    for file in (DATABASE_ROOT / name).glob("*"):
        if file.suffix == ".yaml":
            continue
        # copy file
        relative_path = file.relative_to(DATABASE_ROOT / name)
        temp_folder = TESTING_DIR / name / "temp"
        temp_folder.mkdir(exist_ok=True)
        shutil.copy(file, temp_folder / relative_path)
