import shutil
from pathlib import Path

import pytest
import yaml
from load_atoms.database.processing import Chain, SelectFile, UnZip, parse_steps


def test_all_steps():
    raw = """
- UnZip
- SelectFile:
    file: "file.txt"
- ReadASE
- Custom:
    id: 1-dummy
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


def test_unzip(tmp_path):
    # make a zip file
    (tmp_path / "test_unzip").mkdir(exist_ok=True, parents=True)
    (tmp_path / "test_unzip" / "file.txt").write_text("fake file")

    # zip the test_unzip folder into tmp_path / "archive.zip"
    shutil.make_archive(tmp_path / "archive", "zip", tmp_path / "test_unzip")

    # unzip it
    extracted_dir = UnZip(file="archive.zip")(tmp_path)
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
    extracted_dir = UnZip()(tmp_path)
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
