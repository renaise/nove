"""API request/response schemas using Pydantic."""

from pydantic import BaseModel, Field

# ============================================================================
# Body Analysis
# ============================================================================


class BodyMeasurements(BaseModel):
    """Body measurements in inches."""

    bust: float = Field(..., description="Bust circumference in inches")
    waist: float = Field(..., description="Waist circumference in inches")
    hips: float = Field(..., description="Hip circumference in inches")


class SilhouetteRecommendation(BaseModel):
    """A recommended dress silhouette with score and reasoning."""

    type: str = Field(..., description="Silhouette type (mermaid, a-line, etc.)")
    score: float = Field(..., ge=0.0, le=1.0, description="Match score 0-1")
    reason: str = Field(..., description="Why this silhouette is recommended")


class BodyAnalysisResult(BaseModel):
    """Complete body analysis results."""

    measurements: BodyMeasurements
    estimated_size: int = Field(..., description="Estimated US bridal dress size")
    size_range: str = Field(..., description="Likely size range (e.g., '6-10')")
    body_type: str = Field(..., description="Body type classification")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Analysis confidence")


class AnalyzeBodyRequest(BaseModel):
    """Request to analyze body from photo(s)."""

    images: list[str] = Field(..., min_length=1, max_length=3, description="Base64-encoded images")
    user_id: str | None = Field(None, description="Optional user ID for storage")


class AnalyzeBodyResponse(BaseModel):
    """Response from body analysis."""

    body_analysis: BodyAnalysisResult
    mesh_preview_url: str | None = Field(None, description="URL to 3D mesh preview")
    recommended_silhouettes: list[SilhouetteRecommendation]


# ============================================================================
# Dress Recommendations
# ============================================================================


class PriceRange(BaseModel):
    """Price range filter."""

    min: int = Field(0, ge=0, description="Minimum price in dollars")
    max: int = Field(100000, ge=0, description="Maximum price in dollars")


class DressRecommendationRequest(BaseModel):
    """Request for dress recommendations."""

    silhouettes: list[str] = Field(..., min_length=1, description="Silhouette types")
    user_size: int = Field(..., ge=0, le=30, description="User's dress size")
    price_range: PriceRange | None = None
    limit: int = Field(10, ge=1, le=50, description="Max results to return")


class DressInfo(BaseModel):
    """Dress information for recommendations."""

    id: str
    name: str
    silhouette: str
    price: int = Field(..., description="Price in dollars")
    brand: str | None = None
    image_url: str
    size_min: int
    size_max: int
    tags: list[str] = []


class DressRecommendationResponse(BaseModel):
    """Response with dress recommendations."""

    dresses: list[DressInfo]
    total_available: int = Field(..., description="Total matching dresses")


# ============================================================================
# Try-On Generation
# ============================================================================


class GenerateTryOnRequest(BaseModel):
    """Request to generate try-on preview."""

    user_photo: str = Field(..., description="Base64-encoded photo or URL")
    dress_id: str = Field(..., description="Dress ID to try on")


class GenerateTryOnResponse(BaseModel):
    """Response from try-on generation."""

    tryon_image_url: str = Field(..., description="URL to generated try-on image")
    generation_id: str = Field(..., description="ID for this generation")
