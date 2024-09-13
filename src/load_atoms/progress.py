from __future__ import annotations

import os
from datetime import timedelta
from typing import Protocol

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


class Task(Protocol):
    def update(self, **kwargs):
        ...

    def __enter__(self) -> Task:
        ...

    def __exit__(self, *args):
        ...


class Progress(Protocol):
    def __init__(self, title: str):
        ...

    def new_task(
        self,
        description: str,
        total: int | float | None = None,
    ) -> Task:
        """Add a new task to the progress bar."""
        ...

    def add_text(self, text: str):
        """Add a text row to the progress bar."""

    def refresh(self):
        """Refresh the progress bar."""

    def __enter__(self) -> Progress:
        """Enter the context manager."""
        ...

    def __exit__(self, *args):
        """Exit the context manager."""
        ...


def get_progress_for_dataset(dataset_id: str) -> Progress:
    if os.environ.get("LOAD_ATOMS_VERBOSE") == "0":
        return SilentProgress(dataset_id)
    return VisibleProgress(dataset_id)


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


class VisibleProgress(Progress):
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
    ) -> VisibleTask:
        return VisibleTask(
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


class VisibleTask:
    def __init__(self, task_id: TaskID, progress: RichProgress):
        self._task_id = task_id
        self._progress = progress

    def update(self, **kwargs):
        self._progress.update(self._task_id, **kwargs)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self._progress.update(self._task_id, completed=True, total=1)


class SilentTask:
    def __init__(self, description: str, total: int | float | None = None):
        ...

    def update(self, **kwargs):
        ...

    def __enter__(self) -> Task:
        return self

    def __exit__(self, *args):
        ...


class SilentProgress(Progress):
    def __init__(self, title: str):
        ...

    def new_task(
        self, description: str, total: int | float | None = None
    ) -> Task:
        return SilentTask(description, total)

    def add_text(self, text: str):
        ...

    def refresh(self):
        ...

    def __enter__(self):
        return self

    def __exit__(self, *args):
        ...
