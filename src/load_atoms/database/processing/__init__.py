from __future__ import annotations

import importlib
import shutil
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Generic, TypeVar

import yaml
from ase import Atoms
from ase.io import read as ase_read
from rich.progress import track

X, Y = TypeVar("X"), TypeVar("Y")


class Step(ABC, Generic[X, Y]):
    """
    Represents a single step in a processing
    :class:`~load_atoms.database.processing.Chain`.
    """

    @abstractmethod
    def __call__(self, x: X) -> Y:
        """Perform the step, transforming the input into the output."""
        ...


class Chain(Generic[X, Y]):
    """
    Represents a chain of processing steps.

    Parameters
    ----------
    steps
        The steps to perform in order.
    """

    def __init__(self, steps: list[Step]):
        self.steps = steps

    def __call__(self, x: X) -> Y:
        """Perform the steps in order."""
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
    default = """\
- ForEachFile:
    steps:
      - ReadASE: {}
"""
    return parse_steps(yaml.safe_load(default))


@register_step
class UnZip(Step[Path, Path]):
    """
    UnZips an archive folder, and returns the path to the extracted folder.

    Parameters
    ----------
    file
        The name of the file to extract. If not provided, it is assumed that
        only a single archive file is present in the directory.

    Examples
    --------
    Unzip the downloaded file:

    .. code-block:: yaml

            processing:
            - UnZip

    Unzip a specific file:

    .. code-block:: yaml

        processing:
            - UnZip:
                file: "archive.zip"

    Behaviour:

    >>> UnZip()(Path("root"))
    Path("root/extracted")
    """

    def __init__(self, file: str | None = None):
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
    """
    Alters the input path to point to a specific file.

    Parameters
    ----------
    file
        The name of the file to select.

    Examples
    --------
    Select a specific file:

    .. code-block:: yaml

        processing:
            - SelectFile:
                file: "file.txt"

    Behaviour:

    >>> SelectFile("file.txt")(Path("root"))
    Path("root/file.txt")
    """

    def __init__(self, file: str):
        self.file = file

    def __call__(self, root: Path) -> Path:
        return root / self.file

    def __repr__(self):
        return f"SelectFile({self.file})"


@register_step
class ForEachFile(Step[Path, "list[Atoms]"]):
    """
    Apply a chain of processing steps to each file in a directory.

    Parameters
    ----------
    steps
        The steps to apply to each file.
    files
        The files to apply the steps to. If not provided, all files in the
        directory are processed.
    pattern
        A pattern to match files in the directory. If not provided, all files
        in the directory are processed.

    Examples
    --------
    Apply a chain of processing steps to all files in a directory:

    .. code-block:: yaml

        processing:
            - ForEachFile:
                steps:
                  - ReadASE: {}
                files:
                  - "file1.xyz"
                  - "file2.xyz"
    """

    def __init__(
        self,
        steps: list[str | dict[str, dict[str, str]]],
        files: list[str] | None = None,
        pattern: str | None = None,
    ):
        self.chain = parse_steps(steps)
        self.files = files
        self.pattern = pattern

    def __call__(self, root: Path) -> list[Atoms]:
        if self.files is not None:
            files = [root / file for file in self.files]
        elif self.pattern is not None:
            files = sorted(root.glob(self.pattern))
        else:
            files = sorted(root.iterdir())

        results = []
        for file in track(
            files,
            description="Processing files",
        ):
            results.extend(self.chain(file))
        return results


@register_step
class ReadASE(Step[Path, "list[Atoms]"]):
    """
    Read the atoms from an ASE-readable file.

    Parameters
    ----------
    kwargs
        Additional keyword arguments to pass to :func:`ase.io.read`.

    Examples
    --------
    Read all atoms from an xyz file:

    .. code-block:: yaml

        processing:
            - SelectFile:
                file: "structures.xyz"
            - ReadASE

    Behaviour:

    >>> ReadASE()(Path("root/structures.xyz"))
    [Atoms(...), Atoms(...), ...]
    """

    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def __call__(self, file: Path) -> list[Atoms]:
        return ase_read(file, index=":", **self.kwargs)  # type: ignore

    def __repr__(self):
        return f"ReadASE({self.kwargs})"


@register_step
class Custom(Step[Path, "list[Atoms]"]):
    """
    Apply a custom processing function for a dataset.

    This should be implemented in
    :code:`load_atoms.database.processing.custom.<id>::process`, taking the
    path to the download directory as an argument, and returning a list of
    :code:`ase.Atoms` objects.

    Parameters
    ----------

    id
        The id of the custom processing function to apply.

    Examples
    --------

    Apply a custom processing function:

    .. code-block:: yaml

        processing:
            - Custom:
                id: "<id>"
    """

    def __init__(self, id: str):
        self.id = id
        try:
            self.func = importlib.import_module(
                f"load_atoms.database.processing.{self.id}"
            ).process
        except ModuleNotFoundError:
            raise ValueError(f"Unknown custom processing: {self.id}") from None

    def __call__(self, file: Path) -> list[Atoms]:
        return self.func(file)

    def __repr__(self):
        return f"Custom({self.id})"
