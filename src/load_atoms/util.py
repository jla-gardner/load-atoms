from pathlib import Path
from typing import Iterable

# this file is at load_atoms/src/load_atoms/util.py
# the datasets are at load_atoms/datasets
DATASETS_DIR = Path(__file__).parent.parent.parent / "datasets"
DEFAULT_DOWNLOAD_DIR = Path.home() / ".load_atoms"
BASE_REMOTE_URL = "https://github.com/jla-gardner/load-atoms/raw/main/datasets/"

DONE = "█"
TODO = "░"


def lpad(s, indent=4):
    return "\n".join(" " * indent + line for line in s.splitlines())


def intersection(things: Iterable[Iterable]):
    """Get the set intersection of a list of iterables."""
    return set.intersection(*map(set, things))


def progress_bar(iterable, N, width=50):
    """own implementation of tqdm for download progress bar"""

    def _progress(count, total):
        progress = min(count / total, 1)

        parts = int(progress * width)
        done = DONE * parts
        todo = TODO * (width - parts)

        message = f"{progress:6.1%} | {done}{todo}"
        print(message, end="\r")

    _progress(0, N)
    for i, item in enumerate(iterable):
        yield item
        _progress(i + 1, N)
    print()
