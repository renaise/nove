"""AI Orchestrator using Claude Opus 4.5 for intelligent image analysis and decision-making"""

import anthropic
import base64
from pathlib import Path
from typing import Optional
from .config import get_settings
from .models import ImageQuality, StitchAnalysis


class OpusOrchestrator:
    """Orchestrates image processing using Claude Opus 4.5 for intelligent analysis"""

    def __init__(self):
        settings = get_settings()
        self.client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        self.model = settings.anthropic_model

    def _encode_image(self, image_path: Path) -> tuple[str, str]:
        """Encode image to base64 for Claude API"""
        with open(image_path, "rb") as f:
            image_data = f.read()

        # Detect media type
        suffix = image_path.suffix.lower()
        media_type_map = {
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".webp": "image/webp",
            ".gif": "image/gif"
        }
        media_type = media_type_map.get(suffix, "image/jpeg")

        encoded = base64.standard_b64encode(image_data).decode("utf-8")
        return encoded, media_type

    async def analyze_bride_silhouette(self, image_path: Path) -> ImageQuality:
        """
        Analyze bride silhouette image using Opus 4.5

        Validates:
        - A-pose detection
        - Image clarity and lighting
        - Privacy concerns (face visibility)
        - Body segmentation feasibility
        """
        image_data, media_type = self._encode_image(image_path)

        prompt = """You are an expert computer vision validator for a bridal gown virtual try-on system.

Analyze this bride silhouette image and assess:

1. **Pose Quality**: Is the person in an A-pose (arms slightly away from body, legs together)?
2. **Image Clarity**: Is the image sharp, well-lit, and high enough resolution?
3. **Background**: Is the background simple enough for clean segmentation?
4. **Privacy**: Is the face visible (privacy concern) or properly obscured?
5. **Body Segmentation**: Can you clearly distinguish body contours for garment fitting?

Provide your assessment as JSON:
{
  "is_valid": true/false,
  "score": 0.0-1.0,
  "issues": ["list of problems found"],
  "recommendations": ["how to improve the photo"]
}

Be strict - only mark as valid if the image will produce high-quality try-on results."""

        message = self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            messages=[{
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": image_data,
                        },
                    },
                    {
                        "type": "text",
                        "text": prompt
                    }
                ],
            }],
        )

        # Parse the response
        response_text = message.content[0].text

        # Extract JSON from response (handle markdown code blocks)
        import json
        import re

        json_match = re.search(r'```json\s*(\{.*?\})\s*```', response_text, re.DOTALL)
        if json_match:
            result = json.loads(json_match.group(1))
        else:
            # Try to parse as direct JSON
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group(0))
            else:
                # Fallback - assume invalid
                result = {
                    "is_valid": False,
                    "score": 0.0,
                    "issues": ["Could not parse AI response"],
                    "recommendations": ["Please try a clearer image"]
                }

        return ImageQuality(**result)

    async def analyze_boutique_garment(self, image_path: Path, garment_name: str) -> ImageQuality:
        """
        Analyze boutique garment image using Opus 4.5

        Validates:
        - Background separation (white dress vs white wall challenge)
        - Garment completeness (full dress visible)
        - Lighting consistency
        - Fabric detail visibility
        """
        image_data, media_type = self._encode_image(image_path)

        prompt = f"""You are an expert validator for a bridal boutique inventory digitization system.

Analyze this image of a bridal gown (named: "{garment_name}") on a mannequin and assess:

1. **Background Separation**: Can the white/ivory dress be clearly distinguished from the background?
2. **Garment Completeness**: Is the full dress visible (hem to neckline)?
3. **Lighting**: Is the lighting even and professional?
4. **Fabric Details**: Are lace, beading, and fabric textures clearly visible?
5. **Mannequin**: Is it a standard bridal mannequin suitable for anchor point mapping?

Provide your assessment as JSON:
{{
  "is_valid": true/false,
  "score": 0.0-1.0,
  "issues": ["list of problems found"],
  "recommendations": ["how to improve the photo"]
}}

Be strict - this image will be used for AI-powered virtual try-ons, so quality is critical."""

        message = self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            messages=[{
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": image_data,
                        },
                    },
                    {
                        "type": "text",
                        "text": prompt
                    }
                ],
            }],
        )

        response_text = message.content[0].text

        # Parse JSON from response
        import json
        import re

        json_match = re.search(r'```json\s*(\{.*?\})\s*```', response_text, re.DOTALL)
        if json_match:
            result = json.loads(json_match.group(1))
        else:
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group(0))
            else:
                result = {
                    "is_valid": False,
                    "score": 0.0,
                    "issues": ["Could not parse AI response"],
                    "recommendations": ["Please try a clearer image"]
                }

        return ImageQuality(**result)

    async def orchestrate_tryon(
        self,
        silhouette_path: Path,
        garment_path: Path
    ) -> StitchAnalysis:
        """
        Orchestrate the virtual try-on process using Opus 4.5

        This analyzes both images and provides intelligent guidance on:
        - Size compatibility
        - Style matching
        - Processing parameters
        - Expected result quality
        """
        silhouette_data, silhouette_type = self._encode_image(silhouette_path)
        garment_data, garment_type = self._encode_image(garment_path)

        prompt = """You are an AI orchestrator for a virtual try-on system.

You have two images:
1. A bride's body silhouette
2. A bridal gown on a mannequin

Analyze both and provide orchestration guidance:

1. **Size Compatibility**: Does the garment appear compatible with the body shape?
2. **Style Analysis**: Describe the dress style and how it might look on this body type
3. **Processing Recommendations**: What adjustments should the warping algorithm prioritize?
4. **Quality Prediction**: How confident are you the try-on will look realistic?

Provide your analysis as JSON:
{
  "analysis_type": "tryon_orchestration",
  "confidence": 0.0-1.0,
  "insights": ["key observations about the match"],
  "actions_taken": ["recommended processing steps"],
  "metadata": {
    "size_compatibility": "excellent/good/fair/poor",
    "style_notes": "description of the dress",
    "predicted_quality": "high/medium/low"
  }
}

Your insights will help optimize the rendering pipeline."""

        message = self.client.messages.create(
            model=self.model,
            max_tokens=2048,
            messages=[{
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Bride Silhouette:"
                    },
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": silhouette_type,
                            "data": silhouette_data,
                        },
                    },
                    {
                        "type": "text",
                        "text": "Bridal Gown:"
                    },
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": garment_type,
                            "data": garment_data,
                        },
                    },
                    {
                        "type": "text",
                        "text": prompt
                    }
                ],
            }],
        )

        response_text = message.content[0].text

        # Parse JSON from response
        import json
        import re

        json_match = re.search(r'```json\s*(\{.*?\})\s*```', response_text, re.DOTALL)
        if json_match:
            result = json.loads(json_match.group(1))
        else:
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group(0))
            else:
                result = {
                    "analysis_type": "tryon_orchestration",
                    "confidence": 0.5,
                    "insights": ["Analysis completed"],
                    "actions_taken": ["Processing images"],
                    "metadata": {}
                }

        return StitchAnalysis(**result)
