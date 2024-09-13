from load_atoms.database.backend import SingleFileImporter
from load_atoms.database.internet import FileDownload


class Importer(SingleFileImporter):
    @classmethod
    def file_to_download(cls) -> FileDownload:
        return FileDownload(
            url="https://zenodo.org/record/4003703/files/P_GAP_20_fitting_data.xyz",
            expected_hash="ab3059018068",
        )
