"""FastAPI application entry point (the outermost adapter).

Responsibilities are limited to framework wiring: middleware, routers, exception
translation and static file serving. All real logic lives in inner layers.
"""
from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.core.exceptions import HealthVisionError
from app.core.logging import configure_logging, get_logger
from app.interfaces.api.routes import analysis, dashboard, health

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    settings.STORAGE_DIR.mkdir(parents=True, exist_ok=True)
    logger.info("%s starting (env=%s)", settings.APP_NAME, settings.APP_ENV)
    yield
    logger.info("%s shutting down", settings.APP_NAME)


app = FastAPI(
    title=settings.APP_NAME,
    description=(
        "Educational HealthTech demo that classifies chest X-ray images. "
        "This project is for educational and portfolio purposes only. "
        "It is NOT a medical diagnosis tool."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=list(settings.CORS_ORIGINS),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(HealthVisionError)
async def healthvision_error_handler(
    request: Request, exc: HealthVisionError
) -> JSONResponse:
    logger.warning("Domain error on %s: %s", request.url.path, exc.message)
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message, "type": exc.__class__.__name__},
    )


# Routers
app.include_router(health.router)
app.include_router(analysis.router, prefix=settings.API_V1_PREFIX)
app.include_router(dashboard.router, prefix=settings.API_V1_PREFIX)

# Serve uploaded images so the frontend can render them.
settings.STORAGE_DIR.mkdir(parents=True, exist_ok=True)
app.mount(
    "/uploads", StaticFiles(directory=str(settings.STORAGE_DIR)), name="uploads"
)


@app.get("/", tags=["root"])
async def root() -> dict[str, str]:
    return {
        "name": settings.APP_NAME,
        "docs": "/docs",
        "disclaimer": (
            "This project is for educational and portfolio purposes only. "
            "It is not a medical diagnosis tool."
        ),
    }
