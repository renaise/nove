"""Pydantic models for API requests and responses"""

from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime
from enum import Enum


class ProcessingStatus(str, Enum):
    """Status of image processing pipeline"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ImageQuality(BaseModel):
    """Image quality assessment from Opus"""
    is_valid: bool
    score: float = Field(ge=0.0, le=1.0)
    issues: list[str] = []
    recommendations: list[str] = []


class BrideSilhouetteRequest(BaseModel):
    """Request for bride silhouette processing"""
    image_id: str
    privacy_mode: bool = True


class BrideSilhouetteResponse(BaseModel):
    """Response after bride silhouette processing"""
    silhouette_id: str
    status: ProcessingStatus
    quality: Optional[ImageQuality] = None
    processed_at: datetime
    message: str


class BoutiqueGarmentRequest(BaseModel):
    """Request for boutique garment processing"""
    image_id: str
    garment_name: str
    boutique_id: str


class BoutiqueGarmentResponse(BaseModel):
    """Response after boutique garment processing"""
    garment_id: str
    status: ProcessingStatus
    quality: Optional[ImageQuality] = None
    processed_at: datetime
    message: str


class TryOnRequest(BaseModel):
    """Request for virtual try-on"""
    silhouette_id: str
    garment_id: str
    render_quality: Literal["fast", "standard", "high"] = "standard"


class TryOnResponse(BaseModel):
    """Response for virtual try-on request"""
    tryon_id: str
    status: ProcessingStatus
    render_url: Optional[str] = None
    processing_time_ms: Optional[int] = None
    created_at: datetime
    message: str


class StitchAnalysis(BaseModel):
    """AI analysis from Opus 4.5"""
    analysis_type: str
    confidence: float = Field(ge=0.0, le=1.0)
    insights: list[str]
    actions_taken: list[str]
    metadata: dict = {}
