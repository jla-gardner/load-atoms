from __future__ import annotations

from datetime import timedelta

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


class Progress:
    def __init__(self, description: str, transient: bool = False):
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
                title=f"[bold]{description}",
            ),
            refresh_per_second=10,
            transient=transient,
        )

    def new_task(
        self,
        description: str,
        transient: bool = False,
        total: int | float | None = None,
        **kwargs,
    ) -> Task:
        return Task(
            self._progress.add_task(description, total=total, **kwargs),
            self._progress,
            transient,
        )

    def log_below(self, text: str, align: str = "center"):
        self._table.add_row(Align(Text.from_markup(text), align=align))  # type: ignore

    def __enter__(self):
        self._live.__enter__()
        return self

    def __exit__(self, *args):
        self._progress.refresh()
        self._live.refresh()
        self._live.__exit__(*args)


class Task:
    def __init__(self, task: TaskID, progress: RichProgress, transient: bool):
        self._task = task
        self._progress = progress
        self._transient = transient

    def update(self, **kwargs):
        self._progress.update(self._task, **kwargs)

    def complete(self, remove: bool = False):
        self._progress.update(self._task, completed=True, total=1)
        if remove:
            self._progress.remove_task(self._task)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        if args[0] is None:
            self.complete(remove=self._transient)
