from pages import (
    _DOC_SOURCE,
    _PROJECT_ROOT,
    build_datasets_index,
    build_docs_page_for,
)

if __name__ == "__main__":
    for file in (_DOC_SOURCE / "datasets").glob("*.rst"):
        file.unlink()
    for dataset_dir in sorted((_PROJECT_ROOT / "database").iterdir()):
        if not dataset_dir.is_dir():
            continue
        build_docs_page_for(dataset_dir.stem)
    build_datasets_index()
