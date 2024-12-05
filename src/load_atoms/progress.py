from __future__ import annotations

import os
import sys
from abc import ABC, abstractmethod
from datetime import timedelta
from typing import Generic, TypeVar

from rich.align import Align
from rich.live import Live
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    ProgressColumn,
    SpinnerColumn,
    TaskID,
    TextColumn,
)
from rich.progress import Progress as RichProgress
from rich.table import Column, Table
from rich.text import Text


class Task:
    def update(self, **kwargs):
        ...

    def __enter__(self) -> Task:
        return self

    def __exit__(self, *args):
        ...


T = TypeVar("T", bound=Task)


class Progress(Generic[T], ABC):
    def __init__(self, title: str):
        ...

    @abstractmethod
    def new_task(
        self,
        description: str,
        total: int | float | None = None,
    ) -> T:
        """Add a new task to the progress bar."""

    def add_text(self, text: str):
        """Add a text row to the progress bar."""

    def refresh(self):
        """Refresh the progress bar."""

    def __enter__(self) -> Progress:
        """Enter the context manager."""
        return self

    def __exit__(self, *args):
        """Exit the context manager."""

    def bold(self, text: str) -> str:
        """Return the text in bold."""
        return text

    def link(self, text: str, url: str) -> str:
        """Return the text as a link."""
        return url


def get_progress_for_dataset(dataset_id: str) -> Progress:
    if os.environ.get("LOAD_ATOMS_VERBOSE") == "0":
        return SilentProgress(dataset_id)

    # check if in colab notebook: rich progress bar
    # doesn't appear to work well there
    if "google.colab" in sys.modules:
        return PrintedProgressBar(dataset_id)

    return RichProgressBar(dataset_id)


class TimeElapsedColumn(ProgressColumn):
    """Renders time elapsed."""

    def render(self, task) -> Text:
        elapsed = task.finished_time if task.finished else task.elapsed
        if elapsed is None:
            return Text("--:--", style="black")
        delta = timedelta(seconds=int(elapsed))
        return Text(":".join(str(delta).split(":")[1:]), style="black")


class PercentColumn(ProgressColumn):
    """Renders percentage complete."""

    def render(self, task) -> Text:
        """Show percentage complete."""
        if task.completed is True:
            return Text("100%", style="black")
        if task.total is None:
            return Text("    ")
        return Text(f"{task.percentage:>3.0f}%", style="black")


class RichProgressBar(Progress):
    def __init__(self, title: str):
        self._progress = RichProgress(
            SpinnerColumn(
                spinner_name="point",
                finished_text="[bold green] ✓ [/bold green]",
                speed=0.5,
                style="black",
            ),
            TextColumn(
                "[progress.description]{task.description}",
                table_column=Column(max_width=40, overflow="fold"),
            ),
            BarColumn(bar_width=20),
            PercentColumn(),
            TimeElapsedColumn(),
        )
        self._table = Table.grid()
        self._table.add_row()
        self._table.add_row(Align(self._progress, align="center"))
        self._live = Live(
            Panel.fit(
                self._table,
                title=f"[bold]{title}",
            ),
            refresh_per_second=10,
            transient=False,
        )

    def new_task(
        self,
        description: str,
        total: int | float | None = None,
    ) -> RichProgressBarTask:
        return RichProgressBarTask(
            self._progress.add_task(description, total=total),
            self._progress,
        )

    def add_text(self, text: str):
        self._table.add_row(Align(Text.from_markup(text), align="center"))

    def __enter__(self):
        self._live.__enter__()
        return self

    def __exit__(self, *args):
        self._progress.refresh()
        self._live.refresh()
        self._live.__exit__(*args)

    def refresh(self):
        self._live.refresh()

    def bold(self, text: str) -> str:
        return f"[bold]{text}[/bold]"

    def link(self, text: str, url: str) -> str:
        return f"[dodger_blue2 link={url} underline]{text}[/]"


class RichProgressBarTask(Task):
    def __init__(self, task_id: TaskID, progress: RichProgress):
        self._task_id = task_id
        self._progress = progress

    def update(self, **kwargs):
        self._progress.update(self._task_id, **kwargs)

    def __exit__(self, *args):
        self._progress.update(self._task_id, completed=True, total=1)


class PrintedProgressBar(Progress):
    def __init__(self, title: str):
        self._title = title

    def new_task(
        self, description: str, total: int | float | None = None
    ) -> PrintedTask:
        return PrintedTask(description, total)

    def add_text(self, text: str):
        print(text)

    def __enter__(self):
        # use terminal to underline and make title bold
        title = f"~~ {self._title} ~~"
        title = f"\033[4m\033[1m{title}\033[0m"
        print(title)
        return self

    def bold(self, text: str) -> str:
        # get terminal text in bold
        return f"\033[1m{text}\033[0m"

    def link(self, text: str, url: str) -> str:
        # underline terminal text and make it a link
        return f"\033[4m\033[94m{url}\033[0m"


class PrintedTask(Task):
    def __init__(self, description: str, total: int | float | None = None):
        self._description = description
        self._total = total

    def __enter__(self):
        print(f" - {self._description}...", end="")
        return self

    def __exit__(self, *args):
        print(" ✓")


class SilentTask(Task):
    pass


class SilentProgress(Progress):
    def new_task(
        self, description: str, total: int | float | None = None
    ) -> Task:
        return SilentTask()
