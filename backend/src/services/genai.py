import base64
import logging
from dataclasses import dataclass

from google import genai
from google.genai import types

from src.core.config import settings

logger = logging.getLogger(__name__)


@dataclass
class TryOnResult:
    success: bool
    image_data: bytes | None = None
    error: str | None = None


class GenAIService:
    """Service for generating virtual try-on images using Google GenAI (Nano Banana Pro)."""

    def __init__(self):
        self.client = genai.Client(api_key=settings.google_genai_api_key)
        # Use Nano Banana Pro (Gemini 3 Pro Image) for best quality
        self.model = "gemini-3-pro-image-preview"

    async def generate_try_on(
        self,
        person_image_base64: str,
        dress_image_base64: str,
    ) -> TryOnResult:
        """
        Generate a virtual try-on image combining a person with a wedding dress.

        Args:
            person_image_base64: Base64 encoded image of the person
            dress_image_base64: Base64 encoded image of the wedding dress

        Returns:
            TryOnResult with the generated image or error
        """
        try:
            # Construct the prompt for virtual try-on
            prompt = """You are a professional fashion photographer creating a wedding dress try-on image.

Take the person from the first image and dress them in the wedding dress from the second image.

Requirements:
- Maintain the person's exact face, body shape, skin tone, and pose
- Apply the wedding dress naturally, respecting the body's form and proportions
- Keep the dress details, fabric texture, and embellishments accurate
- Use professional wedding photography lighting
- The result should look like a real photo, not AI-generated
- Maintain high resolution and sharp details

Generate a single, photorealistic image of the person wearing the wedding dress."""

            # Create content parts with both images
            contents = [
                types.Part.from_text(prompt),
                types.Part.from_bytes(
                    data=base64.b64decode(person_image_base64),
                    mime_type="image/jpeg",
                ),
                types.Part.from_bytes(
                    data=base64.b64decode(dress_image_base64),
                    mime_type="image/jpeg",
                ),
            ]

            # Generate the try-on image
            response = await self.client.aio.models.generate_content(
                model=self.model,
                contents=contents,
                config=types.GenerateContentConfig(
                    response_modalities=["IMAGE"],
                    image_generation_config=types.ImageGenerationConfig(
                        aspect_ratio="3:4",  # Portrait orientation for wedding photos
                        image_size="2K",  # High resolution
                    ),
                ),
            )

            # Extract the generated image
            for part in response.candidates[0].content.parts:
                if part.inline_data:
                    return TryOnResult(
                        success=True,
                        image_data=part.inline_data.data,
                    )

            return TryOnResult(
                success=False,
                error="No image was generated in the response",
            )

        except Exception as e:
            logger.exception("Failed to generate try-on image")
            return TryOnResult(
                success=False,
                error=str(e),
            )

    async def generate_try_on_with_url(
        self,
        person_image_url: str,
        dress_image_url: str,
    ) -> TryOnResult:
        """
        Generate a virtual try-on image using image URLs.

        Downloads the images first, then processes them.
        """
        import httpx

        try:
            async with httpx.AsyncClient() as client:
                # Download both images
                person_response = await client.get(person_image_url)
                person_response.raise_for_status()
                person_base64 = base64.b64encode(person_response.content).decode()

                dress_response = await client.get(dress_image_url)
                dress_response.raise_for_status()
                dress_base64 = base64.b64encode(dress_response.content).decode()

            return await self.generate_try_on(person_base64, dress_base64)

        except httpx.HTTPError as e:
            logger.exception("Failed to download images")
            return TryOnResult(
                success=False,
                error=f"Failed to download images: {e}",
            )


# Singleton instance
genai_service = GenAIService()
