"""
Stylist Pipeline - 4-Stage Generative Digital Stylist
Orchestrates the full journey from silhouette to curated recommendations
"""

from pathlib import Path
from datetime import datetime
import time
from ..models import (
    StylistAnalysisResponse,
    ProcessingStatus,
    BodyProportions,
    SilhouetteRecommendation
)
from ..config import get_settings
from ..integrations import SAM3Segmenter
from ..integrations.body_analysis import BodyProportionAnalyzer
from ..integrations.recommendation_engine import SilhouetteRecommendationEngine
from ..integrations.nano_banana import NanoBananaPro


class StylistPipeline:
    """
    The Generative Digital Stylist Pipeline

    4-Stage Flow:
    1. Capture: SAM 3 + MediaPipe for body segmentation
    2. Analysis: Proportion analysis (shoulder-to-waist, waist-to-hip ratios)
    3. Curation: Silhouette matching and recommendations
    4. Vision: Nano Banana Pro for hero renders
    """

    def __init__(self):
        self.settings = get_settings()
        self.sam3 = SAM3Segmenter()
        self.body_analyzer = BodyProportionAnalyzer()
        self.recommendation_engine = SilhouetteRecommendationEngine()
        self.nano_banana = NanoBananaPro()

    async def analyze_and_recommend(
        self,
        image_path: Path,
        generate_hero_renders: bool = True,
        max_recommendations: int = 3
    ) -> StylistAnalysisResponse:
        """
        Run the complete 4-stage stylist analysis

        Args:
            image_path: Path to bride silhouette image
            generate_hero_renders: Whether to generate 3 hero preview renders
            max_recommendations: Number of silhouette recommendations

        Returns:
            StylistAnalysisResponse with full analysis and recommendations
        """
        start_time = time.time()

        # Generate analysis ID
        analysis_id = f"stylist_{int(start_time)}"

        try:
            # ================================================================
            # STAGE 1: CAPTURE (SAM 3 + MediaPipe)
            # ================================================================
            print(f"[Stylist] Stage 1: Capture - Segmenting body with SAM 3...")

            segmentation_quality, segmentation_data = await self.sam3.segment_body(image_path)

            if not segmentation_quality.is_valid:
                return StylistAnalysisResponse(
                    analysis_id=analysis_id,
                    status=ProcessingStatus.FAILED,
                    segmentation_quality=segmentation_quality,
                    processed_at=datetime.utcnow(),
                    message=f"Segmentation failed: {', '.join(segmentation_quality.issues)}",
                    stylist_feedback="We had trouble analyzing your photo. " + ', '.join(segmentation_quality.recommendations)
                )

            landmarks = segmentation_data["landmarks"]

            # ================================================================
            # STAGE 2: ANALYSIS (Body Proportions)
            # ================================================================
            print(f"[Stylist] Stage 2: Analysis - Calculating body proportions...")

            body_proportions = await self.body_analyzer.analyze_proportions(
                image_path,
                landmarks
            )

            # ================================================================
            # STAGE 3: CURATION (Recommendations)
            # ================================================================
            print(f"[Stylist] Stage 3: Curation - Matching silhouettes to body type...")

            recommendations = self.recommendation_engine.recommend_silhouettes(
                body_proportions,
                max_recommendations=max_recommendations
            )

            stylist_feedback = self.recommendation_engine.generate_stylist_feedback(
                body_proportions,
                recommendations
            )

            # ================================================================
            # STAGE 4: VISION (Hero Renders with Nano Banana Pro)
            # ================================================================
            hero_renders = []
            if generate_hero_renders:
                print(f"[Stylist] Stage 4: Vision - Generating hero renders with Nano Banana Pro...")

                recommended_silhouettes = [rec.silhouette_type for rec in recommendations]

                hero_renders = await self.nano_banana.generate_hero_renders(
                    image_path,
                    body_proportions,
                    recommended_silhouettes
                )

            # ================================================================
            # SUCCESS
            # ================================================================
            processing_time = int((time.time() - start_time) * 1000)

            return StylistAnalysisResponse(
                analysis_id=analysis_id,
                status=ProcessingStatus.COMPLETED,
                segmentation_quality=segmentation_quality,
                body_proportions=body_proportions,
                recommendations=recommendations,
                recommended_garment_ids=[],  # Will be populated when we query boutique inventory
                hero_renders=hero_renders,
                processed_at=datetime.utcnow(),
                message=f"Analysis complete in {processing_time}ms. {len(recommendations)} silhouettes recommended.",
                stylist_feedback=stylist_feedback
            )

        except Exception as e:
            return StylistAnalysisResponse(
                analysis_id=analysis_id,
                status=ProcessingStatus.FAILED,
                processed_at=datetime.utcnow(),
                message=f"Analysis failed: {str(e)}",
                stylist_feedback="We encountered an issue analyzing your photo. Please try again with a clear, front-facing photo."
            )
