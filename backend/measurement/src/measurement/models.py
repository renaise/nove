"""Data models for body measurement service."""

from dataclasses import dataclass
from enum import Enum


class BodyType(str, Enum):
    """Wedding dress body type categories."""
    HOURGLASS = "hourglass"  # Bust ≈ Hips, Waist significantly smaller
    PEAR = "pear"  # Hips > Bust
    APPLE = "apple"  # Bust > Hips, less defined waist
    RECTANGLE = "rectangle"  # Bust ≈ Waist ≈ Hips
    INVERTED_TRIANGLE = "inverted_triangle"  # Bust > Hips


@dataclass
class BodyMeasurements:
    """Body measurements in centimeters."""
    # Core measurements for wedding dress sizing
    bust: float  # Fullest part of bust
    waist: float  # Natural waistline
    hips: float  # Fullest part of hips

    # Secondary measurements
    shoulder_width: float  # Shoulder to shoulder
    arm_length: float  # Shoulder to wrist
    torso_length: float  # Shoulder to waist
    inseam: float  # Crotch to ankle

    # Derived
    height_estimate: float  # Estimated height based on proportions
    body_type: BodyType  # Classified body type

    # Confidence
    confidence: float  # 0-1 confidence score

    def to_dict(self) -> dict:
        return {
            "bust_cm": round(self.bust, 1),
            "waist_cm": round(self.waist, 1),
            "hips_cm": round(self.hips, 1),
            "shoulder_width_cm": round(self.shoulder_width, 1),
            "arm_length_cm": round(self.arm_length, 1),
            "torso_length_cm": round(self.torso_length, 1),
            "inseam_cm": round(self.inseam, 1),
            "height_estimate_cm": round(self.height_estimate, 1),
            "body_type": self.body_type.value,
            "confidence": round(self.confidence, 2),
        }

    def get_bridal_size(self) -> dict:
        """Map measurements to standard bridal sizes."""
        # Standard US bridal sizing chart (approximate)
        size_chart = [
            (0, 79, 58, 84),
            (2, 83, 63, 89),
            (4, 86, 66, 92),
            (6, 89, 69, 95),
            (8, 92, 72, 98),
            (10, 95, 75, 101),
            (12, 99, 79, 105),
            (14, 104, 84, 110),
            (16, 109, 89, 115),
            (18, 117, 97, 123),
            (20, 124, 104, 130),
            (22, 132, 112, 138),
            (24, 140, 120, 146),
        ]

        # Find closest size based on largest measurement
        best_size = 10  # Default
        min_diff = float('inf')

        for size, bust, waist, hips in size_chart:
            # Use the measurement that requires the largest size
            diff = max(
                abs(self.bust - bust),
                abs(self.waist - waist),
                abs(self.hips - hips)
            )
            if diff < min_diff:
                min_diff = diff
                best_size = size

        # Also determine size range
        sizes_that_fit = []
        for size, bust, waist, hips in size_chart:
            if (bust >= self.bust - 2 and
                waist >= self.waist - 2 and
                hips >= self.hips - 2):
                sizes_that_fit.append(size)
                if len(sizes_that_fit) >= 2:
                    break

        return {
            "recommended_size": best_size,
            "size_range": sizes_that_fit[:2] if sizes_that_fit else [best_size],
            "note": "Sizes are approximate. Professional fitting recommended.",
        }


@dataclass
class SMPLOutput:
    """Output from SMPL body model."""
    vertices: any  # (6890, 3) mesh vertices
    joints: any  # (24, 3) joint positions
    betas: any  # (10,) shape parameters
    body_pose: any  # (23, 3) pose parameters
    global_orient: any  # (1, 3) global orientation
