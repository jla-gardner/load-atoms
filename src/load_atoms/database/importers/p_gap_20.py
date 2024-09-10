from load_atoms.database.importer import SingleFileImporter


class Importer(SingleFileImporter):
    def __init__(self):
        super().__init__(
            url="https://zenodo.org/record/4003703/files/P_GAP_20_fitting_data.xyz",
            hash="ab3059018068",
        )
