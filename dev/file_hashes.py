"""
This script generates a checksum for a given file/s. If no file is given, it
will generate checksums for all files in the datasets directory.

Usage:
    python dev/file_hashes.py
    python dev/file_hashes.py <path_to_file>
    python dev/file_hashes.py "<glob_pattern>"
"""

import glob
import sys

from load_atoms.checksums import generate_checksum

if __name__ == "__main__":
    try:
        path = sys.argv[1]
    except IndexError:
        path = "src/load_atoms/datasets/*.[!y]*"  # exclude yaml files

    files, checksums = [], []
    for file in glob.glob(path):
        files.append(file)
        checksums.append(generate_checksum(file))

    max_length = max(len(file) for file in files) + 2
    for file, checksum in zip(files, checksums):
        print(f"{file:{max_length}} {checksum}")
