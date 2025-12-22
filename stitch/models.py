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


# ============================================================================
# STYLIST MODELS (V2 - Generative Digital Stylist)
# ============================================================================

class SilhouetteType(str, Enum):
    """Dress silhouette categories"""
    A_LINE = "a_line"
    BALLGOWN = "ballgown"
    MERMAID = "mermaid"
    EMPIRE_WAIST = "empire_waist"
    SHEATH = "sheath"
    TRUMPET = "trumpet"
    TEA_LENGTH = "tea_length"
    COLUMN = "column"


class BodyProportions(BaseModel):
    """Body proportion measurements extracted from silhouette"""
    shoulder_to_waist_ratio: float = Field(ge=0.0, le=2.0, description="Shoulder width to waist ratio")
    waist_to_hip_ratio: float = Field(ge=0.0, le=2.0, description="Waist to hip ratio")
    height_estimate: Optional[str] = Field(None, description="Estimated height category: petite, average, tall")
    body_shape: str = Field(description="Body shape category: hourglass, pear, apple, rectangle, inverted_triangle")
    landmarks: dict = Field(default={}, description="12-point body landmarks from MediaPipe")
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence score of the analysis")


class SilhouetteRecommendation(BaseModel):
    """Silhouette style recommendation with reasoning"""
    silhouette_type: SilhouetteType
    match_score: float = Field(ge=0.0, le=1.0, description="How well this silhouette suits the body type")
    reasoning: str = Field(description="Why this silhouette was recommended")
    styling_tips: list[str] = Field(default=[], description="Specific styling advice")


class StylistAnalysisRequest(BaseModel):
    """Request for full stylist analysis (4-stage pipeline)"""
    image_id: str
    generate_hero_renders: bool = Field(default=True, description="Generate 3 hero preview renders")
    max_recommendations: int = Field(default=3, ge=1, le=5, description="Number of silhouette recommendations")


class StylistAnalysisResponse(BaseModel):
    """Response from stylist analysis with recommendations"""
    analysis_id: str
    status: ProcessingStatus

    # Stage 1: Capture (SAM 3 + MediaPipe)
    segmentation_quality: Optional[ImageQuality] = None

    # Stage 2: Analysis (Body Proportions)
    body_proportions: Optional[BodyProportions] = None

    # Stage 3: Curation (Recommendations)
    recommendations: list[SilhouetteRecommendation] = []
    recommended_garment_ids: list[str] = Field(default=[], description="Pre-filtered garments matching proportions")

    # Stage 4: Vision (Hero Renders)
    hero_renders: list[str] = Field(default=[], description="URLs to 3 generative preview renders")

    # Metadata
    processed_at: datetime
    message: str
    stylist_feedback: str = Field(default="", description="Human-readable feedback for the bride")


class GarmentSilhouetteTag(BaseModel):
    """Boutique garment tagged with silhouette type"""
    garment_id: str
    silhouette_type: SilhouetteType
    best_for_body_shapes: list[str] = Field(default=[], description="Body shapes this dress flatters")
    designer: Optional[str] = None
    price_range: Optional[str] = None


class UpdateBoutiqueGarmentRequest(BaseModel):
    """Request to update garment with silhouette categorization"""
    garment_id: str
    silhouette_type: SilhouetteType
    best_for_body_shapes: list[str] = []
    designer: Optional[str] = None
    price_range: Optional[str] = None
