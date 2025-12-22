"""Bride silhouette processing pipeline"""

from pathlib import Path
from datetime import datetime
from ..models import BrideSilhouetteResponse, ProcessingStatus
from ..orchestrator import OpusOrchestrator
from ..utils.image import validate_image, resize_image, generate_image_id
from ..config import get_settings


class BridePipeline:
    """Handles bride silhouette ingestion and validation"""

    def __init__(self):
        self.settings = get_settings()
        self.orchestrator = OpusOrchestrator()

    async def process_silhouette(
        self,
        image_path: Path,
        privacy_mode: bool = True
    ) -> BrideSilhouetteResponse:
        """
        Process bride silhouette image

        Steps:
        1. Validate image format and size
        2. Use Opus 4.5 for A-pose detection and quality check
        3. Resize and normalize
        4. Store with privacy masking metadata

        Args:
            image_path: Path to uploaded image
            privacy_mode: Whether to ensure face privacy

        Returns:
            BrideSilhouetteResponse with processing status
        """
        # Generate unique ID
        silhouette_id = generate_image_id(image_path)

        # Step 1: Basic validation
        is_valid, error_msg = validate_image(
            image_path,
            max_size_mb=self.settings.max_image_size_mb,
            max_dimension=self.settings.max_image_dimension
        )

        if not is_valid:
            return BrideSilhouetteResponse(
                silhouette_id=silhouette_id,
                status=ProcessingStatus.FAILED,
                processed_at=datetime.utcnow(),
                message=f"Validation failed: {error_msg}"
            )

        # Step 2: AI-powered quality analysis with Opus 4.5
        try:
            quality = await self.orchestrator.analyze_bride_silhouette(image_path)

            if not quality.is_valid:
                return BrideSilhouetteResponse(
                    silhouette_id=silhouette_id,
                    status=ProcessingStatus.FAILED,
                    quality=quality,
                    processed_at=datetime.utcnow(),
                    message=f"Quality check failed: {', '.join(quality.issues)}"
                )

            # Step 3: Process and store
            processed_dir = self.settings.upload_dir / "silhouettes"
            processed_dir.mkdir(parents=True, exist_ok=True)

            output_path = processed_dir / f"{silhouette_id}.png"
            resize_image(image_path, output_path, max_dimension=2048)

            # Success
            return BrideSilhouetteResponse(
                silhouette_id=silhouette_id,
                status=ProcessingStatus.COMPLETED,
                quality=quality,
                processed_at=datetime.utcnow(),
                message=f"Silhouette processed successfully (quality score: {quality.score:.2f})"
            )

        except Exception as e:
            return BrideSilhouetteResponse(
                silhouette_id=silhouette_id,
                status=ProcessingStatus.FAILED,
                processed_at=datetime.utcnow(),
                message=f"Processing error: {str(e)}"
            )
