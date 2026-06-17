"""Async SQLAlchemy engine/session management.

Engines are created lazily (on first use) so that simply importing the ORM
models does not require a database driver to be installed or a database to be
reachable. This keeps unit tests fast and dependency-light while production
code transparently gets a real connection pool.
"""
from __future__ import annotations

from collections.abc import AsyncGenerator
from functools import lru_cache

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import settings


class Base(DeclarativeBase):
    """Declarative base shared by all ORM models."""


# --- Async (API + worker) ---
@lru_cache(maxsize=1)
def get_async_engine():
    return create_async_engine(
        settings.DATABASE_URL,
        echo=settings.DEBUG,
        pool_pre_ping=True,
        future=True,
    )


@lru_cache(maxsize=1)
def _async_sessionmaker_factory() -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(
        bind=get_async_engine(), expire_on_commit=False, class_=AsyncSession
    )


def AsyncSessionLocal() -> AsyncSession:
    """Return a new AsyncSession (callable kept for ergonomic `async with`)."""
    return _async_sessionmaker_factory()()


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency yielding a transactional session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


# --- Sync (Alembic / utilities) ---
@lru_cache(maxsize=1)
def get_sync_engine():
    return create_engine(settings.SYNC_DATABASE_URL, pool_pre_ping=True, future=True)


@lru_cache(maxsize=1)
def _sync_sessionmaker_factory() -> sessionmaker[Session]:
    return sessionmaker(bind=get_sync_engine(), expire_on_commit=False)


def SyncSessionLocal() -> Session:
    return _sync_sessionmaker_factory()()
