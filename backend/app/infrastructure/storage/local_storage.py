"""Local filesystem implementation of the FileStorage port.

In production this would be swapped for an S3 adapter (see docs/architecture.md)
without touching any use case — that is the whole point of the port.
"""
from __future__ import annotations

from pathlib import Path

from app.domain.ports import FileStorage


class LocalFileStorage(FileStorage):
    def __init__(self, base_dir: Path) -> None:
        self._base_dir = Path(base_dir)
        self._base_dir.mkdir(parents=True, exist_ok=True)

    def _path(self, stored_filename: str) -> Path:
        return self._base_dir / stored_filename

    def save(self, stored_filename: str, data: bytes) -> str:
        path = self._path(stored_filename)
        path.write_bytes(data)
        return str(path)

    def read(self, stored_filename: str) -> bytes:
        return self._path(stored_filename).read_bytes()

    def exists(self, stored_filename: str) -> bool:
        return self._path(stored_filename).exists()

    def delete(self, stored_filename: str) -> None:
        self._path(stored_filename).unlink(missing_ok=True)
