"""Seed the database with synthetic analyses so the dashboard is populated.

Generates simple synthetic grayscale "x-ray-like" images (no external dataset
required), stores them, and runs the real inference pipeline inline. This keeps
the demo self-contained while exercising the same code path as production.

Run with:  python -m scripts.seed
"""
from __future__ import annotations

import asyncio
import io

import numpy as np
from app.application.use_cases.process_exam_analysis import (
    ProcessExamAnalysisUseCase,
)
from app.core.config import settings
from app.core.logging import get_logger
from app.core.security import secure_stored_filename
from app.domain.entities.analysis import Analysis
from app.infrastructure.ai.predictor import build_inference_engine
from app.infrastructure.database.repositories.analysis_repository import (
    SqlAlchemyAnalysisRepository,
)
from app.infrastructure.database.session import AsyncSessionLocal
from app.infrastructure.storage.local_storage import LocalFileStorage
from PIL import Image

logger = get_logger(__name__)

SEED_COUNT = 12


def _synthetic_xray(brightness: float, seed: int) -> bytes:
    """Create a 256x256 grayscale image with controllable mean brightness.

    Brightness drives the mock model's output, giving us a mix of NORMAL /
    PNEUMONIA / UNCERTAIN results across the seeded set.
    """
    rng = np.random.default_rng(seed)
    base = np.full((256, 256), int(brightness * 255), dtype=np.uint8)
    noise = rng.normal(0, 18, size=base.shape)
    img = np.clip(base.astype(np.float32) + noise, 0, 255).astype(np.uint8)
    buf = io.BytesIO()
    Image.fromarray(img, mode="L").convert("RGB").save(buf, format="JPEG")
    return buf.getvalue()


async def main() -> None:
    settings.STORAGE_DIR.mkdir(parents=True, exist_ok=True)
    storage = LocalFileStorage(settings.STORAGE_DIR)
    inference = build_inference_engine()

    async with AsyncSessionLocal() as session:
        repo = SqlAlchemyAnalysisRepository(session)
        process = ProcessExamAnalysisUseCase(repo, storage, inference)

        for i in range(SEED_COUNT):
            brightness = (i % 10) / 10.0  # spread 0.0 .. 0.9
            data = _synthetic_xray(brightness, seed=i)
            stored = secure_stored_filename(f"seed_{i}.jpg")
            storage.save(stored, data)
            analysis = Analysis(
                original_filename=f"seed_xray_{i}.jpg",
                stored_filename=stored,
                image_path=f"/uploads/{stored}",
            )
            await repo.add(analysis)
            await session.commit()
            await process.execute(analysis.id)
            await session.commit()
            logger.info("Seeded analysis %s", analysis.id)

    logger.info("Seeding complete: %d analyses", SEED_COUNT)


if __name__ == "__main__":
    asyncio.run(main())
