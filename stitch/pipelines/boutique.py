"""Boutique garment processing pipeline"""

from pathlib import Path
from datetime import datetime
from ..models import BoutiqueGarmentResponse, ProcessingStatus
from ..orchestrator import OpusOrchestrator
from ..utils.image import validate_image, resize_image, generate_image_id
from ..config import get_settings


class BoutiquePipeline:
    """Handles boutique garment ingestion and digitization"""

    def __init__(self):
        self.settings = get_settings()
        self.orchestrator = OpusOrchestrator()

    async def process_garment(
        self,
        image_path: Path,
        garment_name: str,
        boutique_id: str
    ) -> BoutiqueGarmentResponse:
        """
        Process boutique garment image

        Steps:
        1. Validate image format and size
        2. Use Opus 4.5 for background separation analysis
        3. Background removal (simulated - would use SAM 3 in production)
        4. Normalize lighting and store

        Args:
            image_path: Path to uploaded garment image
            garment_name: Name of the dress
            boutique_id: ID of the boutique

        Returns:
            BoutiqueGarmentResponse with processing status
        """
        # Generate unique ID
        garment_id = f"{boutique_id}_{generate_image_id(image_path)}"

        # Step 1: Basic validation
        is_valid, error_msg = validate_image(
            image_path,
            max_size_mb=self.settings.max_image_size_mb,
            max_dimension=self.settings.max_image_dimension
        )

        if not is_valid:
            return BoutiqueGarmentResponse(
                garment_id=garment_id,
                status=ProcessingStatus.FAILED,
                processed_at=datetime.utcnow(),
                message=f"Validation failed: {error_msg}"
            )

        # Step 2: AI-powered quality analysis with Opus 4.5
        try:
            quality = await self.orchestrator.analyze_boutique_garment(
                image_path,
                garment_name
            )

            if not quality.is_valid:
                return BoutiqueGarmentResponse(
                    garment_id=garment_id,
                    status=ProcessingStatus.FAILED,
                    quality=quality,
                    processed_at=datetime.utcnow(),
                    message=f"Quality check failed: {', '.join(quality.issues)}"
                )

            # Step 3: Process and store
            # In production, this would use SAM 3 for background removal
            processed_dir = self.settings.upload_dir / "garments" / boutique_id
            processed_dir.mkdir(parents=True, exist_ok=True)

            output_path = processed_dir / f"{garment_id}.png"
            resize_image(image_path, output_path, max_dimension=2048)

            # Success
            return BoutiqueGarmentResponse(
                garment_id=garment_id,
                status=ProcessingStatus.COMPLETED,
                quality=quality,
                processed_at=datetime.utcnow(),
                message=f"Garment '{garment_name}' processed successfully (quality score: {quality.score:.2f})"
            )

        except Exception as e:
            return BoutiqueGarmentResponse(
                garment_id=garment_id,
                status=ProcessingStatus.FAILED,
                processed_at=datetime.utcnow(),
                message=f"Processing error: {str(e)}"
            )
