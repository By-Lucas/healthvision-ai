"""Model loading abstraction.

Attempts to load real model weights when available; otherwise signals that the
mock should be used. PyTorch is imported lazily so the project still runs (and
tests still pass) in environments where torch is not installed.
"""
from __future__ import annotations

from pathlib import Path

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class LoadedModel:
    """Thin wrapper around a real model + the classes it predicts."""

    def __init__(self, model, classes: list[str]) -> None:
        self.model = model
        self.classes = classes


def try_load_real_model() -> LoadedModel | None:
    """Return a LoadedModel if real weights are configured & loadable, else None."""
    if settings.USE_MOCK_INFERENCE:
        logger.info("USE_MOCK_INFERENCE=True — using mock inference engine.")
        return None

    weights = settings.MODEL_WEIGHTS_PATH
    if not weights or not Path(weights).exists():
        logger.warning(
            "MODEL_WEIGHTS_PATH not found (%s) — falling back to mock engine.",
            weights,
        )
        return None

    try:
        import torch  # noqa: PLC0415
        from torchvision import models  # noqa: PLC0415

        # ResNet18 fine-tuned for 2 classes (NORMAL, PNEUMONIA). UNCERTAIN is
        # produced by the confidence gate, not trained. Matches scripts/train.py.
        model = models.resnet18(weights=None)
        model.fc = torch.nn.Linear(model.fc.in_features, 2)
        state = torch.load(weights, map_location="cpu")
        model.load_state_dict(state)
        model.eval()
        logger.info("Loaded real model from %s", weights)
        return LoadedModel(model, ["NORMAL", "PNEUMONIA"])
    except Exception:  # noqa: BLE001
        logger.exception("Failed to load real model — falling back to mock.")
        return None
