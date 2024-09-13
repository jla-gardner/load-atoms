from __future__ import annotations

from pathlib import Path
from typing import Iterator

import h5py
import numpy as np
from ase import Atoms
from load_atoms.database.backend import BaseImporter, FileDownload
from load_atoms.progress import Progress

Ha_to_eV = 27.2114079527


class Importer(BaseImporter):
    @classmethod
    def permanent_download_dirname(cls) -> str | None:
        return "ANI"  # ensure same as ANI-1x to avoid re-downloading

    @classmethod
    def files_to_download(cls) -> list[FileDownload]:
        return [
            FileDownload(
                url="https://springernature.figshare.com/ndownloader/files/18112775",
                expected_hash="fe0ba06198ee",
                local_name="ani1x-release.h5",
            )
        ]

    @classmethod
    def get_structures(
        cls, tmp_dir: Path, progress: Progress
    ) -> Iterator[Atoms]:
        with h5py.File(tmp_dir / "ani1x-release.h5", "r") as f:
            n_structures = sum(
                (~np.isnan(data["ccsd(t)_cbs.energy"][()])).sum()
                for data in f.values()
            )
            task = progress.new_task(
                "Processing 500k structures",
                total=n_structures,
            )
            ani1x_idx = -1

            # iterate over each chemical formula in the dataset:
            for data in f.values():
                Zs = data["atomic_numbers"]
                coords = data["coordinates"][()]
                cc_energy = data["ccsd(t)_cbs.energy"][()]
                dft_energy = data["wb97x_dz.energy"][()]
                dft_forces = data["wb97x_dz.forces"][()]
                dft_dipole = data["wb97x_dz.dipole"][()]

                for i in range(len(cc_energy)):
                    ani1x_idx += 1

                    if np.isnan(cc_energy[i]):
                        continue

                    structure = Atoms(
                        positions=coords[i],
                        numbers=Zs,
                    )
                    # see: https://www.nature.com/articles/s41597-020-0473-z/tables/2
                    # energy is in hartree, convert to eV
                    structure.info["dft_energy"] = dft_energy[i] * Ha_to_eV
                    structure.info["cc_energy"] = cc_energy[i] * Ha_to_eV
                    # units of e * angstrom
                    structure.info["dft_dipole"] = dft_dipole[i]
                    structure.info["1x_idx"] = ani1x_idx
                    # forces are in hartree/angstrom, convert to eV/angstrom
                    structure.arrays["dft_forces"] = dft_forces[i] * Ha_to_eV

                    task.update(advance=1)
                    yield structure
