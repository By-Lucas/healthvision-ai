"""Optional User entity.

Auth is out of scope for this MVP, but the entity exists so analyses could be
associated with an owner without reworking the domain later.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID, uuid4


@dataclass
class User:
    name: str
    email: str
    id: UUID = field(default_factory=uuid4)
