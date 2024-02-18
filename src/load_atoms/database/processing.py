from __future__ import annotations

import importlib
import shutil
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Callable, Generic, TypeVar

from ase import Atoms
from ase.io import read as ase_read

X, Y = TypeVar("X"), TypeVar("Y")


class Step(ABC, Generic[X, Y]):
    @abstractmethod
    def __call__(self, x: X) -> Y:
        ...


_common_steps: dict[str, type[Step]] = dict()


def register_step(step: type[Step]):
    _common_steps[step.__name__] = step


def get_step_type(name: str) -> type[Step]:
    try:
        return _common_steps[name]
    except KeyError:
        raise ValueError(
            f"Unknown step: {name}. " f"Expected one of {list(_common_steps)}."
        ) from None


def parse_steps(
    raw_steps: list[str | dict[str, dict[str, str]]]
) -> Callable[[Path], list[Atoms]]:
    steps: list[Step] = []

    for step in raw_steps:
        if isinstance(step, str):
            steps.append(get_step_type(step)())
        else:
            name, kwargs = list(step.items())[0]
            steps.append(get_step_type(name)(**kwargs))

    def process(x: Path) -> list[Atoms]:
        for step in steps:
            x = step(x)
        return x  # type: ignore

    return process


@register_step
class UnZip(Step[Path, Path]):
    def __call__(self, file: Path) -> Path:
        extract_to = file.parent / "extracted"
        shutil.unpack_archive(file, extract_dir=extract_to)
        return extract_to


@register_step
class SelectFile(Step[Path, Path]):
    def __init__(self, file: Path):
        super().__init__()
        self.file = file

    def __call__(self, root: Path) -> Path:
        return root / self.file


@register_step
class ReadASE(Step[Path, "list[Atoms]"]):
    def __init__(self, **kwargs):
        super().__init__()
        self.kwargs = kwargs

    def __call__(self, file: Path) -> list[Atoms]:
        return ase_read(file, index=":", **self.kwargs)  # type: ignore


@register_step
class Custom(Step[Path, "list[Atoms]"]):
    def __init__(self, id: str):
        super().__init__()
        self.id = id

    def __call__(self, file: Path) -> list[Atoms]:
        module = importlib.import_module(
            f"load_atoms.processing.custom_processing.{self.id}"
        )
        return module.process(file)
