import sys

from pages import build_datasets_index, build_docs_page_for

if __name__ == "__main__":
    dataset_id = sys.argv[1]
    build_docs_page_for(dataset_id)
    build_datasets_index()
