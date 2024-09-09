from __future__ import annotations

import shutil
from pathlib import Path

import pytest
import yaml
from ase import Atoms
from load_atoms.database.processing import (
    Chain,
    Rename,
    SelectFile,
    Step,
    UnZip,
    parse_steps,
    register_step,
)
from load_atoms.progress import Progress


def test_all_steps():
    raw = """
- UnZip
- SelectFile:
    file: "file.txt"
- ReadASE
- Custom:
    id: 1-dummy
- Rename:
    a: b
"""
    processing_func = parse_steps(yaml.safe_load(raw))
    assert isinstance(processing_func, Chain)


def test_unknown_step():
    raw = """
- UnknownStep
"""
    with pytest.raises(
        ValueError, match="Unknown step: UnknownStep. Expected one of"
    ):
        parse_steps(yaml.safe_load(raw))


@pytest.mark.parametrize(
    "progress",
    (None, Progress("")),
)
def test_unzip(tmp_path, progress):
    # make a zip file
    (tmp_path / "test_unzip").mkdir(exist_ok=True, parents=True)
    (tmp_path / "test_unzip" / "file.txt").write_text("fake file")

    # zip the test_unzip folder into tmp_path / "archive.zip"
    shutil.make_archive(tmp_path / "archive", "zip", tmp_path / "test_unzip")

    # unzip it
    extracted_dir = UnZip(file="archive.zip")(tmp_path, progress)
    assert (extracted_dir / "file.txt").is_file()

    # now test the same thing, but with an implicit file
    # remove everything in the tmp_path except the archive
    for file in tmp_path.iterdir():
        if file.name != "archive.zip":
            if file.is_dir():
                shutil.rmtree(file)
            else:
                file.unlink()

    assert next(tmp_path.iterdir()).name == "archive.zip"
    extracted_dir = UnZip()(tmp_path, progress)
    assert (extracted_dir / "file.txt").is_file()


def test_select_file():
    root = Path("root")
    selected = SelectFile(file="file.txt")(root)
    assert selected == root / "file.txt"


def test_custom_step():
    raw = """
- Custom:
    id: 1-dummy
"""
    func = parse_steps(yaml.safe_load(raw))
    assert callable(func)
    assert func(Path("unused")) is not None

    raw = """
- Custom:
    id: unknown
"""
    with pytest.raises(ValueError, match="Unknown custom processing"):
        parse_steps(yaml.safe_load(raw))


def test_rename():
    structure = Atoms("H2")
    structure.info["a"] = 1.23
    structure.arrays["y"] = [1, 2]

    Rename(a="b", y="z")([structure])

    assert "a" not in structure.info
    assert structure.info["b"] == 1.23

    assert "y" not in structure.arrays
    assert structure.arrays["z"] == [1, 2]


@pytest.mark.parametrize(
    "progress",
    (None, Progress("")),
)
def test_for_each_file(tmp_path, progress):
    # make a few files
    (tmp_path / "file1.txt").write_text("file1")
    (tmp_path / "file2.txt").write_text("file2")
    (tmp_path / "file3.csv").write_text("a,b,c")

    @register_step
    class DummyStep(Step):
        def __call__(self, file: Path, progress: None = None) -> list[str]:  # type: ignore
            return [file.stem]

    # test with no kwargs
    raw = """
- ForEachFile:
    steps:
        - DummyStep
"""
    func = parse_steps(yaml.safe_load(raw))
    result = func(tmp_path, progress)
    assert result == ["file1", "file2", "file3"]

    # test with files
    raw = """
- ForEachFile:
    steps:
        - DummyStep
    files:
        - file3.csv
"""
    func = parse_steps(yaml.safe_load(raw))
    result = func(tmp_path, progress)
    assert result == ["file3"]

    # test with pattern
    raw = """
- ForEachFile:
    steps:
        - DummyStep
    pattern: "*.txt"
"""
    func = parse_steps(yaml.safe_load(raw))
    result = func(tmp_path, progress)
    assert result == ["file1", "file2"]
