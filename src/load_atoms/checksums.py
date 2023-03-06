import hashlib
from pathlib import Path


def generate_checksum(file_path: Path) -> str:
    """Generate a checksum for a file."""

    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)

    return sha256_hash.hexdigest()[:12]