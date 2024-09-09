from load_atoms.database.importer import BASE_GITHUB_URL, SingleFileImporter


class Importer(SingleFileImporter):
    def __init__(self):
        super().__init__(
            url=f"{BASE_GITHUB_URL}/C-GAP-17/C-GAP-17.extxyz",
            hash="8dd037b59c88",
        )
