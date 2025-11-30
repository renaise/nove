import enum
from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, Enum, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base


class TryOnStatus(enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class TryOnRequest(Base):
    __tablename__ = "try_on_requests"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid4())
    )

    # Input images
    person_image_url: Mapped[str] = mapped_column(String(500))
    dress_id: Mapped[str] = mapped_column(String(36))

    # Workflow tracking
    status: Mapped[TryOnStatus] = mapped_column(
        Enum(TryOnStatus), default=TryOnStatus.PENDING
    )
    temporal_workflow_id: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Result
    result_image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Metadata
    user_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
