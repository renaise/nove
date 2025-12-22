"""
Nove Stitch Engine - Main FastAPI Application
AI-orchestrated virtual try-on pipeline using Claude Opus 4.5
"""

from fastapi import FastAPI, UploadFile, File, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from pathlib import Path
import shutil
from datetime import datetime
from typing import List
import json

from .config import get_settings
from .models import (
    BrideSilhouetteRequest,
    BrideSilhouetteResponse,
    BoutiqueGarmentRequest,
    BoutiqueGarmentResponse,
    TryOnRequest,
    TryOnResponse,
    ProcessingStatus,
    # V2: Stylist Models
    StylistAnalysisRequest,
    StylistAnalysisResponse,
    UpdateBoutiqueGarmentRequest,
    GarmentSilhouetteTag
)
from .pipelines.bride import BridePipeline
from .pipelines.boutique import BoutiquePipeline
from .pipelines.tryon import TryOnPipeline
from .pipelines.stylist import StylistPipeline

# Initialize app
app = FastAPI(
    title="Nove Stitch Engine",
    description="AI-orchestrated generative digital stylist for bridal gowns",
    version="0.2.0"
)

# Get settings
settings = get_settings()

# Ensure directories exist
settings.upload_dir.mkdir(parents=True, exist_ok=True)
settings.temp_dir.mkdir(parents=True, exist_ok=True)

# Mount static files for serving renders
app.mount("/renders", StaticFiles(directory=settings.upload_dir / "renders"), name="renders")
app.mount("/hero_renders", StaticFiles(directory=settings.upload_dir / "hero_renders"), name="hero_renders")

# Initialize pipelines
bride_pipeline = BridePipeline()
boutique_pipeline = BoutiquePipeline()
tryon_pipeline = TryOnPipeline()
stylist_pipeline = StylistPipeline()  # V2: Generative Digital Stylist

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            await connection.send_json(message)

manager = ConnectionManager()


@app.get("/")
async def root():
    """API status endpoint"""
    return {
        "service": "Nove Stitch Engine",
        "version": "0.1.0",
        "status": "operational",
        "ai_model": settings.anthropic_model,
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "uploads_dir": str(settings.upload_dir),
        "temp_dir": str(settings.temp_dir)
    }


# === BRIDE ENDPOINTS ===

@app.post("/bride/upload", response_model=dict)
async def upload_bride_silhouette(file: UploadFile = File(...)):
    """
    Upload bride silhouette image

    Returns image_id for use in processing endpoint
    """
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    # Save temporarily
    temp_path = settings.temp_dir / file.filename
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Generate ID
    from .utils.image import generate_image_id
    image_id = generate_image_id(temp_path)

    # Move to permanent location
    final_path = settings.temp_dir / f"{image_id}{Path(file.filename).suffix}"
    temp_path.rename(final_path)

    return {
        "image_id": image_id,
        "filename": file.filename,
        "message": "Image uploaded successfully. Use /bride/process to validate."
    }


@app.post("/bride/process", response_model=BrideSilhouetteResponse)
async def process_bride_silhouette(request: BrideSilhouetteRequest):
    """
    Process bride silhouette with AI validation

    Uses Claude Opus 4.5 to validate:
    - A-pose detection
    - Image quality
    - Privacy compliance
    """
    # Find image
    image_path = None
    for ext in [".jpg", ".jpeg", ".png", ".webp"]:
        potential_path = settings.temp_dir / f"{request.image_id}{ext}"
        if potential_path.exists():
            image_path = potential_path
            break

    if not image_path:
        raise HTTPException(status_code=404, detail=f"Image not found: {request.image_id}")

    # Process with AI orchestration
    result = await bride_pipeline.process_silhouette(
        image_path,
        privacy_mode=request.privacy_mode
    )

    # Broadcast status via WebSocket
    await manager.broadcast({
        "type": "bride_processing",
        "silhouette_id": result.silhouette_id,
        "status": result.status.value,
        "message": result.message
    })

    return result


# === BOUTIQUE ENDPOINTS ===

@app.post("/boutique/upload", response_model=dict)
async def upload_boutique_garment(file: UploadFile = File(...)):
    """
    Upload boutique garment image

    Returns image_id for use in processing endpoint
    """
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    # Save temporarily
    temp_path = settings.temp_dir / file.filename
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Generate ID
    from .utils.image import generate_image_id
    image_id = generate_image_id(temp_path)

    # Move to permanent location
    final_path = settings.temp_dir / f"{image_id}{Path(file.filename).suffix}"
    temp_path.rename(final_path)

    return {
        "image_id": image_id,
        "filename": file.filename,
        "message": "Image uploaded successfully. Use /boutique/process to validate."
    }


@app.post("/boutique/process", response_model=BoutiqueGarmentResponse)
async def process_boutique_garment(request: BoutiqueGarmentRequest):
    """
    Process boutique garment with AI validation

    Uses Claude Opus 4.5 to validate:
    - Background separation feasibility
    - Garment completeness
    - Image quality
    """
    # Find image
    image_path = None
    for ext in [".jpg", ".jpeg", ".png", ".webp"]:
        potential_path = settings.temp_dir / f"{request.image_id}{ext}"
        if potential_path.exists():
            image_path = potential_path
            break

    if not image_path:
        raise HTTPException(status_code=404, detail=f"Image not found: {request.image_id}")

    # Process with AI orchestration
    result = await boutique_pipeline.process_garment(
        image_path,
        garment_name=request.garment_name,
        boutique_id=request.boutique_id
    )

    # Broadcast status via WebSocket
    await manager.broadcast({
        "type": "garment_processing",
        "garment_id": result.garment_id,
        "status": result.status.value,
        "message": result.message
    })

    return result


# === VIRTUAL TRY-ON ENDPOINTS ===

@app.post("/tryon/process", response_model=TryOnResponse)
async def process_tryon(request: TryOnRequest):
    """
    Process virtual try-on request

    Uses Claude Opus 4.5 to orchestrate:
    - Size compatibility analysis
    - Style matching
    - Warping parameter optimization
    """
    # Send initial status via WebSocket
    await manager.broadcast({
        "type": "tryon_started",
        "silhouette_id": request.silhouette_id,
        "garment_id": request.garment_id,
        "status": "processing"
    })

    # Process with AI orchestration
    result = await tryon_pipeline.process_tryon(
        silhouette_id=request.silhouette_id,
        garment_id=request.garment_id,
        render_quality=request.render_quality
    )

    # Broadcast completion via WebSocket
    await manager.broadcast({
        "type": "tryon_completed",
        "tryon_id": result.tryon_id,
        "status": result.status.value,
        "render_url": result.render_url,
        "processing_time_ms": result.processing_time_ms,
        "message": result.message
    })

    return result


# === STYLIST ENDPOINTS (V2: Generative Digital Stylist) ===

@app.post("/stylist/analyze", response_model=StylistAnalysisResponse)
async def analyze_with_stylist(request: StylistAnalysisRequest):
    """
    Full 4-stage Generative Digital Stylist analysis

    Pipeline:
    1. Capture: SAM 3 + MediaPipe for body segmentation
    2. Analysis: Body proportion analysis (shoulder-to-waist, waist-to-hip ratios)
    3. Curation: Silhouette matching and recommendations
    4. Vision: Nano Banana Pro for 3 hero preview renders

    Returns personalized dress silhouette recommendations with styling feedback
    """
    # Find image
    image_path = None
    for ext in [".jpg", ".jpeg", ".png", ".webp"]:
        potential_path = settings.temp_dir / f"{request.image_id}{ext}"
        if potential_path.exists():
            image_path = potential_path
            break

    if not image_path:
        raise HTTPException(status_code=404, detail=f"Image not found: {request.image_id}")

    # Broadcast start
    await manager.broadcast({
        "type": "stylist_analysis_started",
        "image_id": request.image_id,
        "status": "processing"
    })

    # Run full 4-stage analysis
    result = await stylist_pipeline.analyze_and_recommend(
        image_path,
        generate_hero_renders=request.generate_hero_renders,
        max_recommendations=request.max_recommendations
    )

    # Broadcast completion
    await manager.broadcast({
        "type": "stylist_analysis_completed",
        "analysis_id": result.analysis_id,
        "status": result.status.value,
        "recommendations": [
            {"silhouette": rec.silhouette_type.value, "score": rec.match_score}
            for rec in result.recommendations
        ],
        "message": result.message
    })

    return result


@app.post("/boutique/tag-silhouette", response_model=GarmentSilhouetteTag)
async def tag_garment_silhouette(request: UpdateBoutiqueGarmentRequest):
    """
    Tag boutique garment with silhouette type

    Boutiques use this endpoint to categorize their inventory by silhouette type
    (A-Line, Mermaid, Ballgown, etc.) so the stylist can filter and recommend
    appropriate dresses based on body proportions.
    """
    # In production, this would update a database
    # For now, return the tagged garment info
    tag = GarmentSilhouetteTag(
        garment_id=request.garment_id,
        silhouette_type=request.silhouette_type,
        best_for_body_shapes=request.best_for_body_shapes,
        designer=request.designer,
        price_range=request.price_range
    )

    await manager.broadcast({
        "type": "garment_tagged",
        "garment_id": tag.garment_id,
        "silhouette_type": tag.silhouette_type.value
    })

    return tag


# === WEBSOCKET ENDPOINT ===

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time updates

    Clients can connect to receive live updates on:
    - Processing status
    - Render completion
    - Quality check results
    """
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive and handle client messages
            data = await websocket.receive_text()
            message = json.loads(data)

            # Echo back for now (could add client-to-server commands)
            await websocket.send_json({
                "type": "ack",
                "received": message
            })

    except WebSocketDisconnect:
        manager.disconnect(websocket)


# === ERROR HANDLERS ===

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global error handler"""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc),
            "timestamp": datetime.utcnow().isoformat()
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "stitch.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
