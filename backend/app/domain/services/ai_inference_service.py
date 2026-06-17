"""Inference port (the hexagonal "driven" interface).

The domain declares *what* it needs from an AI engine; infrastructure provides
the *how* (mock or a real PyTorch/TensorFlow model). The application layer only
ever talks to this abstract type.
"""
from __future__ import annotations

import abc

from app.domain.value_objects.prediction import Prediction


class AIInferenceService(abc.ABC):
    """Abstract inference engine. Implementations live in infrastructure/ai."""

    @abc.abstractmethod
    def predict(self, image_bytes: bytes) -> Prediction:
        """Run inference on raw image bytes and return a domain Prediction."""
        raise NotImplementedError
