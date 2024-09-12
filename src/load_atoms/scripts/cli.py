import argparse
from pathlib import Path

import ase.io
from load_atoms import load_dataset


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Download a load_atoms dataset from the internet to "
            "a local, `ase.io.read`able file."
        )
    )
    parser.add_argument("dataset_id", help="ID of the dataset to download")
    parser.add_argument(
        "--format",
        default="xyz",
        required=False,
        help="""\
Format to save the dataset in. Must be one of the formats supported by
`ase.io.write`.
""",
    )
    parser.add_argument(
        "--root",
        default=".",
        help="Root directory to save the dataset (default: current directory)",
        required=False,
    )

    args = parser.parse_args()

    # load the dataset in the usual way
    dataset = load_dataset(args.dataset_id)

    if len(dataset) > 10_000:
        print(
            f"""\
warning: {args.dataset_id} has {len(dataset)} structures. 
         Are you sure you want to save this to disk?
         (y/n) """
        )
        response = input()
        if not response.lower().startswith("y"):
            print("Exiting...")
            return

    file_to_write_to = Path(args.root) / f"{args.dataset_id}.{args.format}"
    file_to_write_to.parent.mkdir(parents=True, exist_ok=True)
    ase.io.write(file_to_write_to, dataset)

    print(f"Dataset saved to {file_to_write_to}")
