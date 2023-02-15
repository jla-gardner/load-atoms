from generate_page import build_datasets_index, build_page

from load_atoms.database import DATASETS

if __name__ == "__main__":
    for dataset_id in DATASETS:
        build_page(dataset_id)
    build_datasets_index()
