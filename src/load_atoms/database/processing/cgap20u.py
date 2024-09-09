from load_atoms.database.processing.importer import (
    BASE_GITHUB_URL,
    SingleFileImporter,
)


class Importer(SingleFileImporter):
    def __init__(self):
        super().__init__(
            url=f"{BASE_GITHUB_URL}/C-GAP-20U/C-GAP-20U.xyz",
            hash="da0462802df1",
        )
