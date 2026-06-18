import hashlib 
from pathlib import Path

def compute_sha256(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()

def compute_sha256_from_file(file_path: Path, chunk_size: int = 8192) -> str:
    hasher = hashlib.sha256()
    with file_path.open("rb") as f:
        while chunk := f.read(chunk_size):
            hasher.update(chunk)
    return hasher.hexdigest()
        