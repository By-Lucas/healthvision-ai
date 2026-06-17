"""Block until the database accepts connections, then exit 0.

Used as a startup gate in docker-compose so migrations / the worker never race
the Postgres container. Complements (does not replace) the compose healthcheck.

Run with:  python -m scripts.wait_for_db
"""
from __future__ import annotations

import sys
import time

from app.core.logging import get_logger
from app.infrastructure.database.session import get_sync_engine
from sqlalchemy import text

logger = get_logger(__name__)

MAX_ATTEMPTS = 60
DELAY_SECONDS = 2


def main() -> int:
    engine = get_sync_engine()
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info("Database is ready (attempt %d).", attempt)
            return 0
        except Exception as exc:  # noqa: BLE001
            logger.warning(
                "Database not ready (attempt %d/%d): %s",
                attempt,
                MAX_ATTEMPTS,
                exc.__class__.__name__,
            )
            time.sleep(DELAY_SECONDS)
    logger.error("Database did not become ready in time.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
