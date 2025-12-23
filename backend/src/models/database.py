"""Database models for the Novia backend."""

from datetime import datetime
from typing import Any
from uuid import uuid4

from sqlalchemy import JSON, DateTime, Index, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from src.config import settings


class Base(AsyncAttrs, DeclarativeBase):
    """Base class for all database models."""

    pass


class Dress(Base):
    """Wedding dress catalog entry."""

    __tablename__ = "dresses"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4())
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    silhouette: Mapped[str] = mapped_column(String(50), nullable=False)
    price_cents: Mapped[int] = mapped_column(Integer, nullable=False)
    brand: Mapped[str | None] = mapped_column(String(255), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    image_url: Mapped[str] = mapped_column(String(512), nullable=False)
    thumbnail_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    size_min: Mapped[int] = mapped_column(Integer, nullable=False)
    size_max: Mapped[int] = mapped_column(Integer, nullable=False)
    tags: Mapped[list[Any]] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    __table_args__ = (
        Index("idx_dresses_silhouette", "silhouette"),
        Index("idx_dresses_price", "price_cents"),
        Index("idx_dresses_sizes", "size_min", "size_max"),
    )


class BodyAnalysis(Base):
    """Stored body analysis results for a user."""

    __tablename__ = "body_analyses"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4())
    )
    user_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    bust: Mapped[float] = mapped_column(nullable=False)
    waist: Mapped[float] = mapped_column(nullable=False)
    hips: Mapped[float] = mapped_column(nullable=False)
    body_type: Mapped[str] = mapped_column(String(50), nullable=False)
    estimated_size: Mapped[int] = mapped_column(Integer, nullable=False)
    confidence: Mapped[float] = mapped_column(nullable=False)
    mesh_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


# Database engine and session
engine = create_async_engine(settings.database_url, echo=settings.debug)
async_session = async_sessionmaker(engine, expire_on_commit=False)


async def get_db():
    """Dependency to get database session."""
    async with async_session() as session:
        yield session
