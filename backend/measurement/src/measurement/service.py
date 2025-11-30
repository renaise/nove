"""
Body Measurement Service.

Two approaches available:
1. MediaPipe Pose (default) - Fast, reliable, works out of the box
2. HMR 2.0 + SMPL - More accurate but requires trained weights
"""

import io
from pathlib import Path
from typing import Optional, Union

import numpy as np
from PIL import Image

from .models import BodyMeasurements


class MeasurementService:
    """
    Service for extracting body measurements from photos.

    Default pipeline (MediaPipe):
    1. Load image
    2. Detect body landmarks with MediaPipe Pose
    3. Compute measurements from landmark positions + user height

    Alternative pipeline (HMR 2.0):
    1. Load image
    2. Run HMR 2.0 to get SMPL mesh
    3. Extract measurements from mesh vertices
    """

    def __init__(self, use_hmr: bool = False, lazy_load: bool = True):
        """
        Initialize the measurement service.

        Args:
            use_hmr: If True, use HMR 2.0 instead of MediaPipe (requires trained weights)
            lazy_load: If True, defer model loading until first use
        """
        self._use_hmr = use_hmr
        self._hmr_model = None
        self._pose_model = None
        self._lazy_load = lazy_load

        if not lazy_load:
            self._load_models()

    def _load_models(self):
        """Load required models."""
        if self._use_hmr:
            self._load_hmr()
        else:
            self._load_pose()

    def _load_hmr(self):
        """Load HMR 2.0 model."""
        if self._hmr_model is None:
            from .hmr import load_model
            print("Loading HMR 2.0 model (this may take a moment)...")
            self._hmr_model = load_model()
            print("HMR model loaded!")

    def _load_pose(self):
        """Load MediaPipe Pose model."""
        if self._pose_model is None:
            from .pose_measurement import get_pose_measurement
            print("Loading MediaPipe Pose model...")
            self._pose_model = get_pose_measurement()
            print("Pose model loaded!")

    def measure_from_image(
        self,
        image: Union[str, Path, bytes, Image.Image],
        user_height_cm: Optional[float] = None,
    ) -> BodyMeasurements:
        """
        Extract body measurements from an image.

        Args:
            image: Input image (path, bytes, or PIL Image)
            user_height_cm: User's height in cm for accurate scaling
                           If not provided, measurements are relative estimates

        Returns:
            BodyMeasurements object with all measurements
        """
        # Load image
        pil_image = self._load_image(image)

        if self._use_hmr:
            return self._measure_with_hmr(pil_image, user_height_cm)
        else:
            return self._measure_with_pose(pil_image, user_height_cm)

    def _measure_with_pose(
        self,
        image: Image.Image,
        user_height_cm: Optional[float],
    ) -> BodyMeasurements:
        """Measure using MediaPipe Pose."""
        if self._pose_model is None:
            self._load_pose()

        return self._pose_model.measure(image, user_height_cm)

    def _measure_with_hmr(
        self,
        image: Image.Image,
        user_height_cm: Optional[float],
    ) -> BodyMeasurements:
        """Measure using HMR 2.0 + SMPL."""
        if self._hmr_model is None:
            self._load_hmr()

        from .anthropometry import extract_measurements

        # Run HMR 2.0 to get mesh
        vertices, joints, params = self._hmr_model.predict(
            image,
            user_height_cm=user_height_cm,
        )

        # Extract measurements from mesh
        return extract_measurements(
            vertices=vertices,
            scale_factor=100.0,
            user_height_cm=user_height_cm,
        )

    def _load_image(
        self,
        image: Union[str, Path, bytes, Image.Image],
    ) -> Image.Image:
        """Load image from various input types."""
        if isinstance(image, Image.Image):
            return image
        elif isinstance(image, bytes):
            return Image.open(io.BytesIO(image))
        elif isinstance(image, (str, Path)):
            return Image.open(image)
        else:
            raise ValueError(f"Unsupported image type: {type(image)}")


# Global service instance (lazy loaded)
_service: Optional[MeasurementService] = None


def get_service() -> MeasurementService:
    """Get or create the global measurement service."""
    global _service
    if _service is None:
        _service = MeasurementService(lazy_load=True)
    return _service


def measure(
    image: Union[str, Path, bytes, Image.Image],
    user_height_cm: Optional[float] = None,
) -> BodyMeasurements:
    """
    Convenience function to measure body from image.

    Args:
        image: Input image
        user_height_cm: User's height for accurate scaling

    Returns:
        BodyMeasurements object
    """
    return get_service().measure_from_image(image, user_height_cm)
