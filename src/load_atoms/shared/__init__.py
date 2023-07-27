class UnknownDatasetException(Exception):
    def __init__(self, dataset_id):
        super().__init__(f"Unknown dataset: {dataset_id}")


BASE_REMOTE_URL = (
    "https://github.com/jla-gardner/load-atoms/raw/main/src/load_atoms/datasets/"
)
