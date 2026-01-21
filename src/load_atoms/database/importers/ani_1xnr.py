from __future__ import annotations

from pathlib import Path
from typing import Iterator

import h5py
from ase import Atoms
from ase.data import atomic_numbers as element_to_atomic_num_dict
from load_atoms.database.backend import (
    BaseImporter,
    FileDownload,
)
from load_atoms.progress import Progress

Ha_to_eV = 27.2114079527


def load_ani1xnr_subset_structures(iter_group: h5py.Group, task):

    for data in iter_group.values():

        # iterate over each structure in each subset
        elements = data["species"][()]
        coords = data["coordinates"][()]
        dft_energy = data["energy"][()]
        dft_forces = data["forces"][()]
        cell = data["cell"][()][0]

        Zs = [element_to_atomic_num_dict[element.decode()] for element in elements]

        for i in range(coords.shape[0]):
            structure = Atoms(positions=coords[i], numbers=Zs)
            
            # energy is in hartree, convert to eV
            structure.set_cell(cell)
            structure.info["energy"] = dft_energy[i] * Ha_to_eV

            # forces are in hartree/angstrom, convert to eV/angstrom
            structure.arrays["forces"] = dft_forces[i] * Ha_to_eV

            task.update(advance=1)
            yield structure


class Importer(BaseImporter):
    @classmethod
    def files_to_download(cls) -> list[FileDownload]:
        return [
            FileDownload(
                url="https://springernature.figshare.com/ndownloader/files/43190004",
                expected_hash="fe0ba06198ee",
                local_name="ani1xnr.h5",
            )
        ]

    @classmethod
    def permanent_download_dirname(cls) -> str | None:
        # ensure this file download is persisted so that we don't
        # have to re-download the same file for the ANI-1ccx dataset
        return "ANI_1xnr"

    @classmethod
    def get_structures(
        cls, tmp_dir: Path, progress: Progress
    ) -> Iterator[Atoms]:

        with h5py.File(tmp_dir / "ani1xnr.h5", "r") as f:

            task = progress.new_task(
                "Processing 26 650 structures",
                total=26650,
            )
            print("Task Type: ", type(task))

            # handle first iterations data
            for iter_name, iter_group in f.items():

                if iter_name != "nano-data-it1-6.h5":
                    yield from load_ani1xnr_subset_structures(iter_group, task)

            # handle nano-data
            for iter_group in f["nano-data-it1-6.h5"].values():
                yield from load_ani1xnr_subset_structures(iter_group, task)
