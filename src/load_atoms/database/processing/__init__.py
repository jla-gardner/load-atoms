from __future__ import annotations

import importlib
import shutil
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Generic, TypeVar

from ase import Atoms
from ase.io import read as ase_read

X, Y = TypeVar("X"), TypeVar("Y")


class Step(ABC, Generic[X, Y]):
    @abstractmethod
    def __call__(self, x: X) -> Y:
        ...


class Chain(Generic[X, Y]):
    def __init__(self, steps: list[Step]):
        self.steps = steps

    def __call__(self, x: X) -> Y:
        for step in self.steps:
            x = step(x)
        return x  # type: ignore

    def __repr__(self):
        return f"Chain({', '.join(str(step) for step in self.steps)})"


_common_steps: dict[str, type[Step]] = dict()


def register_step(step: type[Step]):
    _common_steps[step.__name__] = step
    return step


def get_step_type(name: str) -> type[Step]:
    try:
        return _common_steps[name]
    except KeyError:
        raise ValueError(
            f"Unknown step: {name}. " f"Expected one of {list(_common_steps)}."
        ) from None


def parse_steps(
    raw_steps: list[str | dict[str, dict[str, str]]]
) -> Chain[Path, list[Atoms]]:
    steps: list[Step] = []

    for step in raw_steps:
        if isinstance(step, str):
            steps.append(get_step_type(step)())
        else:
            name, kwargs = list(step.items())[0]
            steps.append(get_step_type(name)(**kwargs))

    return Chain(steps)


def default_processing():
    return [
        {
            "ForEachFile": {
                "steps": [
                    {"ReadASE": {}},
                ]
            },
        }
    ]


@register_step
class UnZip(Step[Path, Path]):
    def __init__(self, file: Path | None = None):
        self.file = file

    def __call__(self, root: Path) -> Path:
        if self.file is None:
            # get the first (and only) file in the directory
            extract_from = next(root.iterdir())
        else:
            extract_from = root / self.file
        extract_to = root / "extracted"
        shutil.unpack_archive(extract_from, extract_dir=extract_to)
        return extract_to

    def __repr__(self):
        return "UnZip()" if self.file is None else f"UnZip({self.file})"


@register_step
class SelectFile(Step[Path, Path]):
    def __init__(self, file: Path):
        self.file = file

    def __call__(self, root: Path) -> Path:
        return root / self.file

    def __repr__(self):
        return f"SelectFile({self.file})"


@register_step
class ForEachFile(Step[Path, "list[Atoms]"]):
    def __init__(self, steps: list[str | dict[str, dict[str, str]]]):
        self.chain = parse_steps(steps)

    def __call__(self, root: Path) -> list[Atoms]:
        return sum(
            (self.chain(file) for file in root.iterdir()),
            start=[],
        )


@register_step
class ReadASE(Step[Path, "list[Atoms]"]):
    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def __call__(self, file: Path) -> list[Atoms]:
        return ase_read(file, index=":", **self.kwargs)  # type: ignore

    def __repr__(self):
        return f"ReadASE({self.kwargs})"


@register_step
class Custom(Step[Path, "list[Atoms]"]):
    def __init__(self, id: str):
        self.id = id

    def __call__(self, file: Path) -> list[Atoms]:
        module = importlib.import_module(
            f"load_atoms.database.processing.{self.id}"
        )
        return module.process(file)

    def __repr__(self):
        return f"Custom({self.id})"
