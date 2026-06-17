"""Data Transfer Objects used between application and interface layers."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class DashboardSummary:
    total_analyses: int = 0
    average_confidence: float = 0.0
    by_class: dict[str, int] = field(default_factory=dict)
    by_status: dict[str, int] = field(default_factory=dict)
