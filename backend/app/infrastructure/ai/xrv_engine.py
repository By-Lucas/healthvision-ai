"""Real chest X-ray inference using torchxrayvision.

torchxrayvision ships DenseNet models pretrained on a union of large public
chest X-ray datasets (NIH, CheXpert, MIMIC, RSNA, etc.). The model is
multi-label (one sigmoid probability per pathology), and "Pneumonia",
"Consolidation" and "Lung Opacity" are among its outputs — exactly the findings
that characterize pneumonia on a radiograph.

This engine implements the same `AIInferenceService` port as the mock, so the
rest of the application is unchanged. Heavy imports (torch, torchxrayvision) are
deferred to call time so environments without them (e.g. CI unit tests) keep
working with the mock.
"""
from __future__ import annotations

import io
import time

import numpy as np

from app.core.config import settings
from app.core.logging import get_logger
from app.domain.services.ai_inference_service import AIInferenceService
from app.domain.value_objects.prediction import PredictedClass, Prediction

logger = get_logger(__name__)

# Pathologies that, on a chest X-ray, are consistent with pneumonia. We take the
# strongest signal among them so a pneumonia that the model labels primarily as
# "Lung Opacity"/"Consolidation" is still caught.
_PNEUMONIA_SIGNALS = ("Pneumonia", "Consolidation", "Lung Opacity")


class TorchXRayVisionEngine(AIInferenceService):
    def __init__(self, model, pathologies: list[str]) -> None:
        self._model = model
        self._pathologies = pathologies

    def _preprocess(self, image_bytes: bytes):
        import torchvision  # noqa: PLC0415
        import torchxrayvision as xrv  # noqa: PLC0415
        from PIL import Image  # noqa: PLC0415

        # Grayscale float array, then xrv normalization to the [-1024, 1024]
        # range the pretrained models expect.
        img = np.array(
            Image.open(io.BytesIO(image_bytes)).convert("L"), dtype=np.float32
        )
        img = xrv.datasets.normalize(img, 255)
        img = img[None, ...]  # add channel dim -> [1, H, W]
        transform = torchvision.transforms.Compose(
            [xrv.datasets.XRayCenterCrop(), xrv.datasets.XRayResizer(224)]
        )
        return transform(img)  # [1, 224, 224]

    def predict(self, image_bytes: bytes) -> Prediction:
        import torch  # noqa: PLC0415

        started = time.perf_counter()
        img = self._preprocess(image_bytes)
        tensor = torch.from_numpy(img).unsqueeze(0).float()  # [1, 1, 224, 224]
        with torch.no_grad():
            outputs = self._model(tensor)[0].cpu().numpy()

        probs = {p: float(v) for p, v in zip(self._pathologies, outputs, strict=False)}
        pneumonia_score = max(
            (probs.get(name, 0.0) for name in _PNEUMONIA_SIGNALS), default=0.0
        )

        if pneumonia_score >= settings.XRAY_PNEUMONIA_HIGH:
            predicted = PredictedClass.PNEUMONIA
            confidence = pneumonia_score
        elif pneumonia_score <= settings.XRAY_PNEUMONIA_LOW:
            predicted = PredictedClass.NORMAL
            confidence = 1.0 - pneumonia_score
        else:
            predicted = PredictedClass.UNCERTAIN
            confidence = max(pneumonia_score, 1.0 - pneumonia_score)

        elapsed_ms = max(int((time.perf_counter() - started) * 1000), 1)
        logger.info(
            "XRV inference: pneumonia_score=%.3f -> %s", pneumonia_score, predicted
        )
        return Prediction(
            predicted_class=predicted,
            confidence_score=round(float(confidence), 4),
            processing_time_ms=elapsed_ms,
            class_probabilities={
                "NORMAL": round(1.0 - pneumonia_score, 4),
                "PNEUMONIA": round(pneumonia_score, 4),
            },
            # Expose every chest pathology the model scored, not just pneumonia.
            findings={k: round(v, 4) for k, v in probs.items()},
        )


def try_build_xrv_engine() -> TorchXRayVisionEngine | None:
    """Load the torchxrayvision model; return None if unavailable."""
    try:
        import torchxrayvision as xrv  # noqa: PLC0415

        model = xrv.models.DenseNet(weights=settings.XRAY_MODEL_NAME)
        model.eval()
        logger.info("Loaded torchxrayvision model '%s'.", settings.XRAY_MODEL_NAME)
        return TorchXRayVisionEngine(model, list(model.pathologies))
    except Exception:  # noqa: BLE001 - any failure falls back to other engines
        logger.exception(
            "Could not load torchxrayvision model '%s'.", settings.XRAY_MODEL_NAME
        )
        return None
