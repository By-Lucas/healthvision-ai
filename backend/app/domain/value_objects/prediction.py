"""Value objects describing an AI prediction result.

A value object is immutable and has no identity — two predictions with the same
values are interchangeable. This is the contract every inference backend (mock
or real) must return, keeping the domain independent of PyTorch/TensorFlow.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class PredictedClass(str, Enum):
    NORMAL = "NORMAL"
    PNEUMONIA = "PNEUMONIA"
    UNCERTAIN = "UNCERTAIN"


@dataclass(frozen=True, slots=True)
class Prediction:
    predicted_class: PredictedClass
    confidence_score: float  # 0.0 - 1.0
    processing_time_ms: int
    class_probabilities: dict[str, float]
    # All raw model outputs (pathology -> probability). For the real model this
    # holds ~18 chest findings; for the mock it mirrors class_probabilities.
    findings: dict[str, float] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not 0.0 <= self.confidence_score <= 1.0:
            raise ValueError("confidence_score must be between 0 and 1")

    def explanation(self) -> str:
        """A plain-language, non-clinical explanation of the result."""
        pct = round(self.confidence_score * 100, 1)
        if self.predicted_class is PredictedClass.NORMAL:
            return (
                f"The model found patterns most consistent with a NORMAL chest "
                f"X-ray ({pct}% confidence). No pneumonia-like opacities were "
                f"highlighted."
            )
        if self.predicted_class is PredictedClass.PNEUMONIA:
            return (
                f"The model highlighted patterns it associates with PNEUMONIA "
                f"({pct}% confidence), such as lung opacities. This is a "
                f"statistical pattern match, not a diagnosis."
            )
        return (
            f"The model was not confident enough to choose a class "
            f"({pct}% top confidence), so the result is UNCERTAIN. A higher "
            f"quality image may help."
        )
