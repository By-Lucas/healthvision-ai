"""Application configuration loaded from environment variables.

Uses pydantic-settings so configuration is validated and typed. Every value
has a sensible local default so the project boots out-of-the-box, while still
being fully overridable for cloud / production environments.
"""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    # --- App ---
    APP_NAME: str = "HealthVision AI"
    APP_ENV: str = Field(default="local")
    DEBUG: bool = Field(default=True)
    API_V1_PREFIX: str = "/api/v1"

    # --- Database ---
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://healthvision:healthvision@localhost:5432/healthvision"
    )
    # Sync URL used by Alembic / Celery worker bootstrap.
    SYNC_DATABASE_URL: str = Field(
        default="postgresql+psycopg2://healthvision:healthvision@localhost:5432/healthvision"
    )

    # --- Message broker (RabbitMQ) ---
    CELERY_BROKER_URL: str = Field(default="amqp://guest:guest@localhost:5672//")
    CELERY_RESULT_BACKEND: str = Field(default="rpc://")

    # --- Storage ---
    STORAGE_DIR: Path = Field(default=Path("/data/uploads"))

    # --- Uploads / validation ---
    MAX_UPLOAD_SIZE_MB: int = 10
    ALLOWED_CONTENT_TYPES: tuple[str, ...] = ("image/jpeg", "image/png")
    ALLOWED_EXTENSIONS: tuple[str, ...] = (".jpg", ".jpeg", ".png")

    # --- AI ---
    # When MODEL_WEIGHTS_PATH points at a real file the predictor will try to
    # load it; otherwise the project falls back to a deterministic mock so the
    # full pipeline still works without downloading large datasets.
    AI_MODEL_NAME: str = "healthvision-cnn"
    MODEL_WEIGHTS_PATH: str | None = None
    USE_MOCK_INFERENCE: bool = True
    CONFIDENCE_UNCERTAIN_THRESHOLD: float = 0.55

    # --- torchxrayvision (real pretrained chest X-ray model) ---
    # When USE_MOCK_INFERENCE is False, the predictor tries to load this
    # torchxrayvision DenseNet (trained on multiple public chest X-ray datasets)
    # before falling back to a local weights file or, finally, the mock.
    XRAY_MODEL_NAME: str = "densenet121-res224-all"
    # Decision thresholds on the combined pneumonia/opacity probability.
    # >= HIGH ⇒ PNEUMONIA, <= LOW ⇒ NORMAL, in-between ⇒ UNCERTAIN.
    XRAY_PNEUMONIA_HIGH: float = 0.50
    XRAY_PNEUMONIA_LOW: float = 0.35

    # --- CORS ---
    CORS_ORIGINS: tuple[str, ...] = ("http://localhost:5173", "http://localhost:3000")

    @property
    def max_upload_bytes(self) -> int:
        return self.MAX_UPLOAD_SIZE_MB * 1024 * 1024


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
