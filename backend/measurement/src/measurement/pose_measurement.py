"""
Body measurement using MediaPipe Pose landmarks.

This is a simpler, more reliable approach than full HMR when we don't have
trained regression weights. Uses 2D pose landmarks + user height for scaling.
"""

import math
from typing import Optional, Tuple
from dataclasses import dataclass

import cv2
import numpy as np
from PIL import Image

try:
    import mediapipe as mp
    MEDIAPIPE_AVAILABLE = True
except ImportError:
    MEDIAPIPE_AVAILABLE = False

from .models import BodyMeasurements, BodyType


# MediaPipe Pose landmark indices
class PoseLandmark:
    NOSE = 0
    LEFT_EYE_INNER = 1
    LEFT_EYE = 2
    LEFT_EYE_OUTER = 3
    RIGHT_EYE_INNER = 4
    RIGHT_EYE = 5
    RIGHT_EYE_OUTER = 6
    LEFT_EAR = 7
    RIGHT_EAR = 8
    MOUTH_LEFT = 9
    MOUTH_RIGHT = 10
    LEFT_SHOULDER = 11
    RIGHT_SHOULDER = 12
    LEFT_ELBOW = 13
    RIGHT_ELBOW = 14
    LEFT_WRIST = 15
    RIGHT_WRIST = 16
    LEFT_PINKY = 17
    RIGHT_PINKY = 18
    LEFT_INDEX = 19
    RIGHT_INDEX = 20
    LEFT_THUMB = 21
    RIGHT_THUMB = 22
    LEFT_HIP = 23
    RIGHT_HIP = 24
    LEFT_KNEE = 25
    RIGHT_KNEE = 26
    LEFT_ANKLE = 27
    RIGHT_ANKLE = 28
    LEFT_HEEL = 29
    RIGHT_HEEL = 30
    LEFT_FOOT_INDEX = 31
    RIGHT_FOOT_INDEX = 32


@dataclass
class Landmark:
    x: float  # Normalized 0-1
    y: float  # Normalized 0-1
    z: float  # Depth (relative)
    visibility: float  # 0-1


def distance_2d(p1: Landmark, p2: Landmark) -> float:
    """2D Euclidean distance between landmarks (normalized coords)."""
    return math.sqrt((p1.x - p2.x) ** 2 + (p1.y - p2.y) ** 2)


def midpoint(p1: Landmark, p2: Landmark) -> Tuple[float, float]:
    """Midpoint between two landmarks."""
    return ((p1.x + p2.x) / 2, (p1.y + p2.y) / 2)


class PoseMeasurement:
    """
    Extract body measurements from images using MediaPipe Pose.

    This approach:
    1. Detects 33 body landmarks using MediaPipe
    2. Computes proportional measurements from landmark distances
    3. Scales to real measurements using user-provided height

    Measurements are estimated based on anthropometric proportions.
    """

    def __init__(self):
        if not MEDIAPIPE_AVAILABLE:
            raise ImportError("MediaPipe not installed. Run: pip install mediapipe")

        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            static_image_mode=True,
            model_complexity=2,  # Most accurate
            enable_segmentation=False,
            min_detection_confidence=0.5,
        )

    def _get_landmarks(self, image: np.ndarray) -> Optional[list]:
        """Extract pose landmarks from image."""
        # Convert BGR to RGB
        if len(image.shape) == 3 and image.shape[2] == 3:
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        else:
            rgb_image = image

        results = self.pose.process(rgb_image)

        if not results.pose_landmarks:
            return None

        landmarks = []
        for lm in results.pose_landmarks.landmark:
            landmarks.append(Landmark(
                x=lm.x,
                y=lm.y,
                z=lm.z,
                visibility=lm.visibility,
            ))

        return landmarks

    def measure(
        self,
        image: Image.Image,
        user_height_cm: Optional[float] = None,
    ) -> BodyMeasurements:
        """
        Extract body measurements from image.

        Args:
            image: PIL Image (full body, front or side view)
            user_height_cm: User's height for scaling (required for accurate cm)

        Returns:
            BodyMeasurements with estimated measurements
        """
        # Convert PIL to numpy
        img_array = np.array(image)

        # Get landmarks
        landmarks = self._get_landmarks(img_array)

        if landmarks is None:
            raise ValueError("Could not detect body pose in image. "
                           "Ensure full body is visible and well-lit.")

        # Get image dimensions for pixel conversion
        img_h, img_w = image.size[1], image.size[0]

        # Calculate pixel-based distances
        lm = landmarks

        # Shoulder width (in pixels)
        shoulder_width_px = abs(lm[PoseLandmark.LEFT_SHOULDER].x - lm[PoseLandmark.RIGHT_SHOULDER].x) * img_w

        # Hip joint width (MediaPipe gives joint position, not body contour)
        hip_joint_width_px = abs(lm[PoseLandmark.LEFT_HIP].x - lm[PoseLandmark.RIGHT_HIP].x) * img_w

        # Full height: estimate head top to ankle (in pixels)
        # Head top is approximately 5% of body height above nose
        head_top_y = lm[PoseLandmark.NOSE].y - 0.05
        ankle_y = (lm[PoseLandmark.LEFT_ANKLE].y + lm[PoseLandmark.RIGHT_ANKLE].y) / 2
        body_height_px = (ankle_y - head_top_y) * img_h

        # Arm length (shoulder to wrist, average both arms) - in normalized units
        left_arm = (
            distance_2d(lm[PoseLandmark.LEFT_SHOULDER], lm[PoseLandmark.LEFT_ELBOW]) +
            distance_2d(lm[PoseLandmark.LEFT_ELBOW], lm[PoseLandmark.LEFT_WRIST])
        )
        right_arm = (
            distance_2d(lm[PoseLandmark.RIGHT_SHOULDER], lm[PoseLandmark.RIGHT_ELBOW]) +
            distance_2d(lm[PoseLandmark.RIGHT_ELBOW], lm[PoseLandmark.RIGHT_WRIST])
        )
        # Convert to pixels using image diagonal for better accuracy
        img_diag = math.sqrt(img_w**2 + img_h**2)
        arm_length_px = ((left_arm + right_arm) / 2) * img_diag

        # Torso length (shoulder to hip midpoint)
        shoulder_mid_y = (lm[PoseLandmark.LEFT_SHOULDER].y + lm[PoseLandmark.RIGHT_SHOULDER].y) / 2
        hip_mid_y = (lm[PoseLandmark.LEFT_HIP].y + lm[PoseLandmark.RIGHT_HIP].y) / 2
        torso_length_px = (hip_mid_y - shoulder_mid_y) * img_h

        # Inseam (hip to ankle)
        inseam_px = (ankle_y - hip_mid_y) * img_h

        # Calculate scale factor (cm per pixel)
        if user_height_cm and body_height_px > 0:
            scale = user_height_cm / body_height_px
            confidence = 0.75
        else:
            # Assume average female height
            user_height_cm = 165.0
            scale = user_height_cm / body_height_px if body_height_px > 0 else 1.0
            confidence = 0.50

        # Convert linear measurements to cm
        shoulder_width = shoulder_width_px * scale
        arm_length = arm_length_px * scale
        torso_length = torso_length_px * scale
        inseam = inseam_px * scale
        height_estimate = user_height_cm

        # CIRCUMFERENCE ESTIMATION
        # MediaPipe gives skeleton joints, not body contours
        # Hip joint width is unreliable (internal skeleton position)
        # Use shoulder width as primary reference with anthropometric ratios
        #
        # Typical female proportions (research-based):
        # - Shoulder width: 35-42 cm
        # - Bust width: ~shoulder * 0.85
        # - Waist width: ~bust * 0.70-0.80
        # - Hip width: ~bust * 1.05-1.15

        # Estimate body widths from shoulder (most reliable measurement)
        bust_body_width = shoulder_width * 0.85
        waist_body_width = bust_body_width * 0.72  # Typical hourglass ratio
        hip_body_width = bust_body_width * 1.08  # Hips slightly wider than bust

        # Estimate depths (front-to-back) - torso is roughly elliptical
        # Depth/width ratios based on body scanning data
        bust_depth = bust_body_width * 0.72  # Chest is fairly round
        waist_depth = waist_body_width * 0.85  # Waist is rounder
        hip_depth = hip_body_width * 0.78  # Hips are somewhat flat

        # Circumference of ellipse: C ≈ π * sqrt(2 * (a² + b²))
        # where a = width/2, b = depth/2
        def ellipse_circumference(width, depth):
            a, b = width / 2, depth / 2
            return math.pi * math.sqrt(2 * (a**2 + b**2))

        bust = ellipse_circumference(bust_body_width, bust_depth)
        waist = ellipse_circumference(waist_body_width, waist_depth)
        hips = ellipse_circumference(hip_body_width, hip_depth)

        # Classify body type
        body_type = self._classify_body_type(bust, waist, hips)

        return BodyMeasurements(
            bust=bust,
            waist=waist,
            hips=hips,
            shoulder_width=shoulder_width,
            arm_length=arm_length,
            torso_length=torso_length,
            inseam=inseam,
            height_estimate=height_estimate,
            body_type=body_type,
            confidence=confidence,
        )

    def _classify_body_type(self, bust: float, waist: float, hips: float) -> BodyType:
        """Classify body type based on measurements."""
        bust_hip_ratio = bust / hips if hips > 0 else 1.0
        waist_bust_ratio = waist / bust if bust > 0 else 1.0

        if 0.9 <= bust_hip_ratio <= 1.1 and waist_bust_ratio < 0.8:
            return BodyType.HOURGLASS
        elif bust_hip_ratio < 0.9:
            return BodyType.PEAR
        elif bust_hip_ratio > 1.1:
            return BodyType.INVERTED_TRIANGLE
        elif bust_hip_ratio > 1.0 and waist_bust_ratio > 0.8:
            return BodyType.APPLE
        else:
            return BodyType.RECTANGLE

    def close(self):
        """Release resources."""
        self.pose.close()


# Singleton instance
_pose_measurement: Optional[PoseMeasurement] = None


def get_pose_measurement() -> PoseMeasurement:
    """Get or create pose measurement instance."""
    global _pose_measurement
    if _pose_measurement is None:
        _pose_measurement = PoseMeasurement()
    return _pose_measurement


def measure_from_pose(
    image: Image.Image,
    user_height_cm: Optional[float] = None,
) -> BodyMeasurements:
    """
    Convenience function to measure body from image using MediaPipe Pose.

    Args:
        image: PIL Image
        user_height_cm: User's height for scaling

    Returns:
        BodyMeasurements object
    """
    return get_pose_measurement().measure(image, user_height_cm)
