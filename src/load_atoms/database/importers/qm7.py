from load_atoms.database.backend import BASE_GITHUB_URL, SingleFileImporter
from load_atoms.database.internet import FileDownload


class Importer(SingleFileImporter):
    @classmethod
    def file_to_download(cls) -> FileDownload:
        return FileDownload(
            url=f"{BASE_GITHUB_URL}/QM7/QM7.extxyz",
            expected_hash="c9dcec505f4d",
        )
