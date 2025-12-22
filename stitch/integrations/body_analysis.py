"""
Body Proportion Analysis
Analyzes body landmarks to determine proportions and recommend silhouettes
"""

from pathlib import Path
from typing import Dict
import anthropic
from ..config import get_settings
from ..models import BodyProportions


class BodyProportionAnalyzer:
    """
    Analyzes body proportions from segmented image

    Uses AI to determine:
    - Shoulder-to-waist ratio
    - Waist-to-hip ratio
    - Body shape category
    - Height estimate
    """

    def __init__(self):
        settings = get_settings()
        self.client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        self.model = settings.anthropic_model

    def _encode_image(self, image_path: Path) -> tuple[str, str]:
        """Encode image to base64"""
        import base64

        with open(image_path, "rb") as f:
            image_data = f.read()

        suffix = image_path.suffix.lower()
        media_type_map = {
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".webp": "image/webp",
        }
        media_type = media_type_map.get(suffix, "image/jpeg")
        encoded = base64.standard_b64encode(image_data).decode("utf-8")

        return encoded, media_type

    async def analyze_proportions(
        self,
        image_path: Path,
        landmarks: Dict
    ) -> BodyProportions:
        """
        Analyze body proportions from image and landmarks

        Args:
            image_path: Path to silhouette image
            landmarks: Body landmarks from SAM 3

        Returns:
            BodyProportions with ratios and body shape classification
        """
        image_data, media_type = self._encode_image(image_path)

        prompt = f"""You are an expert bridal stylist analyzing body proportions.

Given this silhouette image and body landmarks: {landmarks}

Analyze the body proportions and provide:

1. **Shoulder-to-Waist Ratio**: Measure shoulder width vs waist width (typically 1.2-1.5)
2. **Waist-to-Hip Ratio**: Measure waist width vs hip width (typically 0.7-0.9)
3. **Body Shape**: Classify as one of:
   - hourglass: balanced shoulders/hips, defined waist
   - pear: hips wider than shoulders
   - apple: fuller midsection, less defined waist
   - rectangle: shoulders and hips similar width, less defined waist
   - inverted_triangle: shoulders wider than hips

4. **Height Estimate**: Based on proportions, estimate: petite (<5'4"), average (5'4"-5'8"), tall (>5'8")

Respond in JSON format:
{{
  "shoulder_to_waist_ratio": 1.0-2.0,
  "waist_to_hip_ratio": 0.5-1.5,
  "height_estimate": "petite/average/tall",
  "body_shape": "hourglass/pear/apple/rectangle/inverted_triangle",
  "confidence": 0.0-1.0,
  "analysis_notes": "Brief notes on the body proportions"
}}

Be precise and professional."""

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

        # Parse JSON
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
                # Fallback defaults
                result = {
                    "shoulder_to_waist_ratio": 1.3,
                    "waist_to_hip_ratio": 0.8,
                    "height_estimate": "average",
                    "body_shape": "rectangle",
                    "confidence": 0.5
                }

        return BodyProportions(
            shoulder_to_waist_ratio=result.get("shoulder_to_waist_ratio", 1.3),
            waist_to_hip_ratio=result.get("waist_to_hip_ratio", 0.8),
            height_estimate=result.get("height_estimate", "average"),
            body_shape=result.get("body_shape", "rectangle"),
            landmarks=landmarks,
            confidence=result.get("confidence", 0.5)
        )
