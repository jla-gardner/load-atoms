from load_atoms.database.importer import BASE_GITHUB_URL, SingleFileImporter


class Importer(SingleFileImporter):
    def __init__(self):
        super().__init__(
            url=f"{BASE_GITHUB_URL}/QM7/QM7.extxyz",
            hash="c9dcec505f4d",
        )
