"""API routes for the Novia backend."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.schemas import (
    AnalyzeBodyRequest,
    AnalyzeBodyResponse,
    BodyAnalysisResult,
    BodyMeasurements,
    DressInfo,
    DressRecommendationRequest,
    DressRecommendationResponse,
    GenerateTryOnRequest,
    GenerateTryOnResponse,
    SilhouetteRecommendation,
)
from src.models.database import get_db
from src.services.body_analysis import BodyAnalyzer
from src.services.dress_matcher import get_dress_by_id, get_matching_dresses
from src.services.silhouette import get_all_silhouettes
from src.services.sizing import get_measurement_chart
from src.services.tryon_generator import TryOnGenerator

router = APIRouter(prefix="/api", tags=["api"])

# Service instances
body_analyzer = BodyAnalyzer()
tryon_generator = TryOnGenerator()


@router.post("/analyze-body", response_model=AnalyzeBodyResponse)
async def analyze_body(request: AnalyzeBodyRequest) -> AnalyzeBodyResponse:
    """
    Analyze body from uploaded photo(s).

    Returns measurements, body type, dress size, and silhouette recommendations.
    """
    if not request.images:
        raise HTTPException(status_code=400, detail="At least one image is required")

    # Use the first image for analysis (future: combine multiple views)
    result = await body_analyzer.analyze(request.images[0])

    return AnalyzeBodyResponse(
        body_analysis=BodyAnalysisResult(
            measurements=BodyMeasurements(
                bust=result.measurements.bust,
                waist=result.measurements.waist,
                hips=result.measurements.hips,
            ),
            estimated_size=result.estimated_size,
            size_range=result.size_range,
            body_type=result.body_type.value,
            confidence=result.confidence,
        ),
        mesh_preview_url=result.mesh_url,
        recommended_silhouettes=[
            SilhouetteRecommendation(
                type=rec.silhouette.value,
                score=rec.score,
                reason=rec.reason,
            )
            for rec in result.recommendations
        ],
    )


@router.post("/get-dress-recommendations", response_model=DressRecommendationResponse)
async def get_dress_recommendations(
    request: DressRecommendationRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> DressRecommendationResponse:
    """
    Get dresses matching silhouettes and available in user's size.
    """
    price_min_cents = None
    price_max_cents = None

    if request.price_range:
        price_min_cents = request.price_range.min * 100
        price_max_cents = request.price_range.max * 100

    dresses, total = await get_matching_dresses(
        db,
        request.silhouettes,
        request.user_size,
        price_min_cents=price_min_cents,
        price_max_cents=price_max_cents,
        limit=request.limit,
    )

    return DressRecommendationResponse(
        dresses=[
            DressInfo(
                id=dress.id,
                name=dress.name,
                silhouette=dress.silhouette,
                price=dress.price_cents // 100,
                brand=dress.brand,
                image_url=dress.image_url,
                size_min=dress.size_min,
                size_max=dress.size_max,
                tags=dress.tags or [],
            )
            for dress in dresses
        ],
        total_available=total,
    )


@router.post("/generate-tryon", response_model=GenerateTryOnResponse)
async def generate_tryon(
    request: GenerateTryOnRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> GenerateTryOnResponse:
    """
    Generate a virtual try-on image using Nano Banana Pro (Gemini).
    """
    # Get the dress
    dress = await get_dress_by_id(db, request.dress_id)
    if not dress:
        raise HTTPException(status_code=404, detail="Dress not found")

    # Generate try-on
    result = await tryon_generator.generate(
        user_photo=request.user_photo,
        dress_image_url=dress.image_url,
    )

    return GenerateTryOnResponse(
        tryon_image_url=result.image_url,
        generation_id=result.generation_id,
    )


# ============================================================================
# Reference endpoints
# ============================================================================


@router.get("/silhouettes")
async def list_silhouettes() -> list[dict[str, str]]:
    """Get all available silhouette types with descriptions."""
    return get_all_silhouettes()


@router.get("/size-chart")
async def get_size_chart() -> list[dict[str, float | int]]:
    """Get the bridal sizing chart for reference."""
    return get_measurement_chart()


@router.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy"}
