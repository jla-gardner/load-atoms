from pathlib import Path

DATASETS_DIR = Path(__file__).parent / "datasets"
BASE_REMOTE_URL = (
    "https://github.com/jla-gardner/load-atoms/raw/main/src/load_atoms/datasets/"
)

DONE = "█"
TODO = "░"


def pad(s: str, other: str) -> str:
    return "\n".join(other + line for line in s.splitlines())


def progress_bar(iterable, N):
    """own implementation of tqdm for download progress bar"""

    def _progress(count, total):
        progress = min(count / total, 1)

        tenths = int(progress * 10)
        done = DONE * tenths
        todo = TODO * (10 - tenths)

        message = f"{progress:6.1%} | [{done}{todo}]"
        print(message, end="\r")

    print()

    _progress(0, N)
    for i, item in enumerate(iterable):
        yield item
        _progress(i + 1, N)
    print()
