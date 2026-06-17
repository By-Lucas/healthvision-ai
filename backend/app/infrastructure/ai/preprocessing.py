"""Image preprocessing for inference.

Uses OpenCV + Pillow + NumPy to turn raw bytes into a normalized tensor-ready
array. The exact same pipeline is used whether the mock or a real model runs,
so swapping in real weights requires no preprocessing changes.
"""
from __future__ import annotations

import io

import cv2
import numpy as np
from PIL import Image

TARGET_SIZE = (224, 224)  # standard ImageNet input size for transfer learning
# ImageNet normalization constants (used by most pretrained torchvision models).
_MEAN = np.array([0.485, 0.456, 0.406], dtype=np.float32)
_STD = np.array([0.229, 0.224, 0.225], dtype=np.float32)


def load_rgb(image_bytes: bytes) -> np.ndarray:
    """Decode bytes to an RGB uint8 HxWx3 array."""
    with Image.open(io.BytesIO(image_bytes)) as img:
        return np.array(img.convert("RGB"))


def preprocess(image_bytes: bytes) -> np.ndarray:
    """Return a CHW float32 array normalized for a pretrained CNN."""
    rgb = load_rgb(image_bytes)
    resized = cv2.resize(rgb, TARGET_SIZE, interpolation=cv2.INTER_AREA)
    arr = resized.astype(np.float32) / 255.0
    arr = (arr - _MEAN) / _STD
    # HWC -> CHW
    return np.transpose(arr, (2, 0, 1))


def image_signature(image_bytes: bytes) -> float:
    """A cheap, deterministic [0,1) feature of the image content.

    Used by the mock model so that the same image always yields the same
    prediction (stable demos) while different images differ. It loosely uses
    overall brightness, which is a real (if naive) radiographic signal.
    """
    rgb = load_rgb(image_bytes)
    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
    mean_brightness = float(np.mean(gray)) / 255.0
    return mean_brightness
