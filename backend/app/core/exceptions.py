"""Domain and application level exceptions.

These are transport-agnostic. The API layer translates them into HTTP
responses, keeping the inner layers free of framework concerns.
"""
from __future__ import annotations


class HealthVisionError(Exception):
    """Base class for all application errors."""

    status_code: int = 500
    message: str = "Internal server error"

    def __init__(self, message: str | None = None) -> None:
        super().__init__(message or self.message)
        if message:
            self.message = message


class InvalidImageError(HealthVisionError):
    status_code = 422
    message = "The uploaded file is not a valid medical image."


class FileTooLargeError(HealthVisionError):
    status_code = 413
    message = "The uploaded file exceeds the maximum allowed size."


class UnsupportedFileTypeError(HealthVisionError):
    status_code = 415
    message = "Unsupported file type. Allowed: JPG, JPEG, PNG."


class AnalysisNotFoundError(HealthVisionError):
    status_code = 404
    message = "Analysis not found."


class InferenceError(HealthVisionError):
    status_code = 500
    message = "AI inference failed."
