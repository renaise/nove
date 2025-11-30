"""
FastAPI endpoints for body measurement service.
"""

import io
from typing import Optional

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .service import get_service

app = FastAPI(
    title="Novia Body Measurement API",
    description="AI-powered body measurement extraction from photos",
    version="0.1.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class MeasurementResponse(BaseModel):
    """Response model for measurements."""
    bust_cm: float
    waist_cm: float
    hips_cm: float
    shoulder_width_cm: float
    arm_length_cm: float
    torso_length_cm: float
    inseam_cm: float
    height_estimate_cm: float
    body_type: str
    confidence: float
    bridal_size: dict


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    service: str
    model_loaded: bool


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Check service health."""
    service = get_service()
    return HealthResponse(
        status="healthy",
        service="novia-measurement",
        model_loaded=service._model is not None,
    )


@app.post("/measure", response_model=MeasurementResponse)
async def measure_body(
    image: UploadFile = File(..., description="Photo of person (front view preferred)"),
    height_cm: Optional[float] = Form(
        None,
        description="User's height in centimeters for accurate scaling",
    ),
):
    """
    Extract body measurements from a photo.

    Upload a full-body photo (front view preferred) and optionally provide
    your height for accurate measurements.

    Returns measurements in centimeters and a recommended bridal size.
    """
    # Validate file type
    if image.content_type not in ["image/jpeg", "image/png", "image/webp"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid image type. Supported: JPEG, PNG, WebP",
        )

    try:
        # Read image bytes
        image_bytes = await image.read()

        # Get measurements
        service = get_service()
        measurements = service.measure_from_image(
            image=image_bytes,
            user_height_cm=height_cm,
        )

        # Get bridal size recommendation
        bridal_size = measurements.get_bridal_size()

        return MeasurementResponse(
            bust_cm=round(measurements.bust, 1),
            waist_cm=round(measurements.waist, 1),
            hips_cm=round(measurements.hips, 1),
            shoulder_width_cm=round(measurements.shoulder_width, 1),
            arm_length_cm=round(measurements.arm_length, 1),
            torso_length_cm=round(measurements.torso_length, 1),
            inseam_cm=round(measurements.inseam, 1),
            height_estimate_cm=round(measurements.height_estimate, 1),
            body_type=measurements.body_type.value,
            confidence=round(measurements.confidence, 2),
            bridal_size=bridal_size,
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process image: {str(e)}",
        )


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "Novia Body Measurement API",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/health",
    }
