"""Concrete AIInferenceService implementations.

Two engines implement the same domain port:

* MockInferenceEngine    — deterministic, dependency-light, always available.
* TorchInferenceEngine   — runs a real PyTorch model when weights are provided.

`build_inference_engine()` picks the right one at runtime. Because both return
the same `Prediction` value object, no other layer cares which is active.
"""
from __future__ import annotations

import time

import numpy as np

from app.core.config import settings
from app.core.logging import get_logger
from app.domain.services.ai_inference_service import AIInferenceService
from app.domain.value_objects.prediction import PredictedClass, Prediction
from app.infrastructure.ai import preprocessing
from app.infrastructure.ai.model_loader import LoadedModel, try_load_real_model

logger = get_logger(__name__)

_CLASSES = [PredictedClass.NORMAL, PredictedClass.PNEUMONIA]


def _softmax(x: np.ndarray) -> np.ndarray:
    e = np.exp(x - np.max(x))
    return e / e.sum()


def _build_prediction(
    probs: dict[PredictedClass, float], started: float
) -> Prediction:
    top_class = max(probs, key=probs.get)
    top_score = probs[top_class]

    # Apply an uncertainty gate — a real clinical-grade system would never
    # force a confident answer out of a low-confidence model.
    if top_score < settings.CONFIDENCE_UNCERTAIN_THRESHOLD:
        final_class = PredictedClass.UNCERTAIN
    else:
        final_class = top_class

    elapsed_ms = int((time.perf_counter() - started) * 1000)
    return Prediction(
        predicted_class=final_class,
        confidence_score=round(float(top_score), 4),
        processing_time_ms=max(elapsed_ms, 1),
        class_probabilities={k.value: round(float(v), 4) for k, v in probs.items()},
    )


class MockInferenceEngine(AIInferenceService):
    """Deterministic stand-in for a trained CNN.

    Derives a stable pseudo-probability from a cheap image feature (brightness),
    so the same image always classifies the same way. The output *shape* is
    identical to a real model, which is what lets us swap in real weights later
    with zero downstream changes.
    """

    def predict(self, image_bytes: bytes) -> Prediction:
        started = time.perf_counter()
        signature = preprocessing.image_signature(image_bytes)

        # Map the [0,1) signature onto two class logits in a smooth way.
        normal_logit = 1.0 - signature
        pneumonia_logit = signature
        probs_arr = _softmax(np.array([normal_logit, pneumonia_logit]) * 4.0)
        probs = {
            PredictedClass.NORMAL: probs_arr[0],
            PredictedClass.PNEUMONIA: probs_arr[1],
        }
        logger.debug("Mock inference signature=%.3f probs=%s", signature, probs)
        return _build_prediction(probs, started)


class TorchInferenceEngine(AIInferenceService):
    """Runs a real PyTorch model loaded via model_loader."""

    def __init__(self, loaded: LoadedModel) -> None:
        self._loaded = loaded

    def predict(self, image_bytes: bytes) -> Prediction:
        import torch  # noqa: PLC0415

        started = time.perf_counter()
        arr = preprocessing.preprocess(image_bytes)
        tensor = torch.from_numpy(arr).unsqueeze(0).float()
        with torch.no_grad():
            logits = self._loaded.model(tensor)[0].numpy()
        probs_arr = _softmax(logits[: len(_CLASSES)])
        probs = {cls: probs_arr[i] for i, cls in enumerate(_CLASSES)}
        return _build_prediction(probs, started)


def build_inference_engine() -> AIInferenceService:
    """Select an inference engine at runtime.

    Order when USE_MOCK_INFERENCE is False:
      1. your own fine-tuned weights file (MODEL_WEIGHTS_PATH) — see scripts/train.py
      2. torchxrayvision (real pretrained chest X-ray DenseNet)
      3. the deterministic mock (always available)
    """
    if settings.USE_MOCK_INFERENCE:
        logger.info("USE_MOCK_INFERENCE=True — using mock inference engine.")
        return MockInferenceEngine()

    # A custom fine-tuned model, when provided, wins over the generic one.
    loaded = try_load_real_model()
    if loaded is not None:
        return TorchInferenceEngine(loaded)

    from app.infrastructure.ai.xrv_engine import try_build_xrv_engine  # noqa: PLC0415

    xrv_engine = try_build_xrv_engine()
    if xrv_engine is not None:
        return xrv_engine

    logger.warning("No real model available — falling back to mock engine.")
    return MockInferenceEngine()
