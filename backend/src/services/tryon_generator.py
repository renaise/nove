"""Try-on image generation using Nano Banana Pro (Gemini)."""

import uuid
from dataclasses import dataclass

import httpx

from src.config import settings


@dataclass
class TryOnResult:
    """Result from try-on generation."""

    image_url: str
    generation_id: str


class TryOnGenerator:
    """
    Generates virtual try-on images using Google's Gemini API (Nano Banana Pro).

    This uses Gemini's image generation capabilities to composite a dress
    onto a user's photo.
    """

    def __init__(self, api_key: str | None = None):
        """
        Initialize the try-on generator.

        Args:
            api_key: Gemini API key (defaults to settings)
        """
        self.api_key = api_key or settings.gemini_api_key
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=60.0)
        return self._client

    async def generate(
        self,
        user_photo: str,
        dress_image_url: str,
        *,
        style_prompt: str | None = None,
    ) -> TryOnResult:
        """
        Generate a try-on image.

        Args:
            user_photo: Base64-encoded user photo or URL
            dress_image_url: URL to the dress image
            style_prompt: Optional additional styling instructions

        Returns:
            TryOnResult with generated image URL and generation ID
        """
        generation_id = str(uuid.uuid4())

        # Build the prompt for Gemini
        prompt = self._build_prompt(dress_image_url, style_prompt)

        # TODO: Implement actual Gemini API call
        # This is a stub - replace with actual Nano Banana Pro integration
        #
        # The actual implementation will:
        # 1. Upload user photo to Gemini
        # 2. Send dress reference image
        # 3. Use image generation prompt to create try-on composite
        # 4. Upload result to S3
        # 5. Return S3 URL

        # Placeholder response
        image_url = f"https://cdn.example.com/tryon/{generation_id}.jpg"

        return TryOnResult(
            image_url=image_url,
            generation_id=generation_id,
        )

    def _build_prompt(
        self,
        dress_image_url: str,
        style_prompt: str | None,
    ) -> str:
        """Build the generation prompt."""
        base_prompt = (
            "Create a photorealistic image of the person wearing the wedding dress. "
            "Maintain the person's face, body proportions, and pose. "
            "The dress should fit naturally and look realistic. "
            "Keep the original background and lighting."
        )

        if style_prompt:
            base_prompt += f" Additional styling: {style_prompt}"

        return base_prompt

    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None
