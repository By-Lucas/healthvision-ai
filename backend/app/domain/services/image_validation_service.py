"""Pure domain service that enforces upload rules.

It depends only on configuration values passed in (no framework, no I/O beyond
opening the bytes with Pillow to confirm the file is a real image). This makes
the rules trivially unit-testable.
"""
from __future__ import annotations

import io
from pathlib import Path

from PIL import Image, UnidentifiedImageError

from app.core.exceptions import (
    FileTooLargeError,
    InvalidImageError,
    UnsupportedFileTypeError,
)


class ImageValidationService:
    def __init__(
        self,
        allowed_extensions: tuple[str, ...],
        allowed_content_types: tuple[str, ...],
        max_bytes: int,
    ) -> None:
        self._allowed_extensions = tuple(e.lower() for e in allowed_extensions)
        self._allowed_content_types = allowed_content_types
        self._max_bytes = max_bytes

    def validate(self, *, filename: str, content_type: str | None, data: bytes) -> None:
        self._validate_extension(filename)
        self._validate_content_type(content_type)
        self._validate_size(data)
        self._validate_is_real_image(data)

    def _validate_extension(self, filename: str) -> None:
        suffix = Path(filename).suffix.lower()
        if suffix not in self._allowed_extensions:
            raise UnsupportedFileTypeError(
                f"Extension '{suffix}' not allowed. "
                f"Allowed: {', '.join(self._allowed_extensions)}"
            )

    def _validate_content_type(self, content_type: str | None) -> None:
        if content_type and content_type not in self._allowed_content_types:
            raise UnsupportedFileTypeError(
                f"Content type '{content_type}' not allowed."
            )

    def _validate_size(self, data: bytes) -> None:
        if len(data) == 0:
            raise InvalidImageError("Uploaded file is empty.")
        if len(data) > self._max_bytes:
            raise FileTooLargeError()

    def _validate_is_real_image(self, data: bytes) -> None:
        try:
            with Image.open(io.BytesIO(data)) as img:
                img.verify()
        except (UnidentifiedImageError, OSError, ValueError) as exc:
            raise InvalidImageError("File could not be decoded as an image.") from exc
