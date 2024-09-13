from load_atoms.database.backend import BASE_GITHUB_URL, SingleFileImporter
from load_atoms.database.internet import FileDownload


class Importer(SingleFileImporter):
    @classmethod
    def file_to_download(cls) -> FileDownload:
        return FileDownload(
            url=f"{BASE_GITHUB_URL}/C-GAP-20U/C-GAP-20U.xyz",
            expected_hash="da0462802df1",
        )
