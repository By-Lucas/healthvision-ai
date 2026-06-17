"""Security helpers.

This MVP does not ship full auth (it is a portfolio/educational demo), but the
module exists as the seam where authentication/authorization would live. It
provides a couple of utilities that are genuinely used (filename hashing) and a
placeholder API-key check that can be wired into routes later.
"""
from __future__ import annotations

import hashlib
import secrets
from pathlib import Path


def secure_stored_filename(original_filename: str) -> str:
    """Generate a collision-resistant stored filename, preserving extension."""
    suffix = Path(original_filename).suffix.lower()
    token = secrets.token_hex(16)
    return f"{token}{suffix}"


def hash_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()
