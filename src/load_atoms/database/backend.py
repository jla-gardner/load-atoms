"""
The :code:`backend` module is responsible for down/loading datasets by name, 
storing them locally, and serving them to :code:`load-atoms` via the
:func:`~load_atoms.load_dataset` function.
"""

from __future__ import annotations

import pickle
from pathlib import Path

from ase import Atoms

from load_atoms.database.database_entry import DatabaseEntry, valid_licenses
from load_atoms.database.internet import download
from load_atoms.progress import Progress
from load_atoms.utils import UnknownDatasetException, frontend_url


def load_structures(name: str, root: Path) -> tuple[list[Atoms], DatabaseEntry]:
    """
    Load the structures comprising the dataset with the given id from the
    given path.

    If these structures are not currently present, download and process
    them first.

    Parameters
    ----------
    name
        The id of the dataset to load.
    root
        The root folder to save the structures to.
    """
    with Progress(f"[bold]{name}") as progress:
        result = _load_structures(name, root, progress)
        progress._live.refresh()
    return result


def _load_structures(name, root, progress):
    entry_path = root / name / f"{name}.yaml"
    structures_path = root / name / f"{name}.pkl"
    temp_path = root / name / "temp"

    entry_path.parent.mkdir(parents=True, exist_ok=True)

    # we first need to get the DatabaseEntry for the dataset
    if not (entry_path).exists():
        try:
            download(
                DatabaseEntry.remote_url_for(name),
                entry_path,
                Progress("", transient=True),
            )
        except Exception as e:
            raise UnknownDatasetException(name) from e
    entry = DatabaseEntry.from_yaml_file(entry_path)

    # try to load the structures from disk
    if structures_path.exists():
        with progress.new_task("Reading from disk"), open(
            structures_path, "rb"
        ) as f:
            structures = pickle.load(f)

    # otherwise, import the structures
    else:
        from load_atoms.database.importer import BaseImporter

        # import the "Importer" class from load_atoms.database.importers.<name>
        filename = name.lower().replace("-", "_")
        # TODO: fail nicely if the importer doesn't exist

        importer: BaseImporter = __import__(
            f"load_atoms.database.importers.{filename}",
            fromlist=["Importer"],
        ).Importer()

        structures = list(
            importer.get_dataset(
                root_dir=root / "raw-downloads",
                progress=progress,
            )
        )

        # remove annoying default calculators
        for s in structures:
            s.calc = None

        # cache the structures to disk
        with progress.new_task("Caching to disk"), open(
            structures_path, "wb"
        ) as f:
            pickle.dump(structures, f)

    log_usage_information(entry, progress)

    return structures, entry


def log_usage_information(info: DatabaseEntry, progress: Progress):
    progress.log_below("\n")

    name = f"[bold]{info.name}[/bold]"
    if info.license is not None:
        style = f"dodger_blue2 link={valid_licenses[info.license]} underline"
        progress.log_below(
            f"The {name} dataset is covered by the "
            f"[{style}]{info.license}[/] license."
        )
    if info.citation is not None:
        progress.log_below(
            f"Please cite the {name} dataset " "if you use it in your work."
        )
    progress.log_below(f"For more information about the {name} dataset, visit:")
    url = frontend_url(info)
    url_style = f"dodger_blue2 underline link={url}"
    progress.log_below(f"[{url_style}]load-atoms/{info.name}")
