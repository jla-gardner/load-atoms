from load_atoms.database.importer import BASE_GITHUB_URL, SingleFileImporter


class Importer(SingleFileImporter):
    def __init__(self):
        super().__init__(
            url=f"{BASE_GITHUB_URL}/GST-GAP-22/refitted_GST-GAP-22_PBE.xyz",
            hash="e4c467026dc0",
        )
