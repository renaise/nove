"""
SMPL Anthropometry - Extract body measurements from SMPL mesh.

Based on: https://github.com/DavidBoja/SMPL-Anthropometry
Measurement definitions follow ISO 8559 standard.
"""

import numpy as np
from typing import Optional

from .models import BodyMeasurements, BodyType


# SMPL vertex indices for key anatomical landmarks
# These are standard SMPL topology indices
LANDMARKS = {
    # Head/Neck
    "head_top": 411,
    "neck_base": 3068,

    # Shoulders
    "left_shoulder": 5431,
    "right_shoulder": 1860,

    # Bust/Chest
    "left_bust": 1424,
    "right_bust": 4904,
    "bust_front": 3042,
    "bust_back": 3158,

    # Waist
    "waist_front": 3500,
    "waist_back": 3022,
    "waist_left": 937,
    "waist_right": 4418,

    # Hips
    "hip_front": 3149,
    "hip_back": 3119,
    "hip_left": 856,
    "hip_right": 4343,

    # Arms
    "left_wrist": 5559,
    "right_wrist": 2094,
    "left_elbow": 5325,
    "right_elbow": 1740,

    # Legs
    "left_ankle": 3327,
    "right_ankle": 6728,
    "left_knee": 1009,
    "right_knee": 4505,
    "crotch": 3149,

    # Feet
    "left_heel": 3387,
    "right_heel": 6787,
}

# Vertex loops for circumference measurements
# These trace around the body at specific heights
CIRCUMFERENCE_LOOPS = {
    "bust": [
        3042, 2989, 2964, 1227, 1231, 1319, 1320, 1424, 1302, 1303,
        689, 692, 3049, 3043, 3044, 3050, 4127, 4131, 4767, 4768,
        4904, 4781, 4780, 4168, 4169, 3158, 3157, 3156, 3042
    ],
    "waist": [
        3500, 3502, 1337, 1338, 1339, 937, 938, 939, 3021, 3022,
        3023, 3024, 4420, 4419, 4418, 4821, 4820, 4819, 3503, 3500
    ],
    "hips": [
        3149, 3148, 892, 891, 890, 889, 856, 855, 854, 3119,
        3118, 4343, 4342, 4378, 4377, 4376, 4375, 3150, 3149
    ],
}


def compute_distance(v1: np.ndarray, v2: np.ndarray) -> float:
    """Euclidean distance between two 3D points."""
    return float(np.linalg.norm(v1 - v2))


def compute_circumference(vertices: np.ndarray, loop_indices: list) -> float:
    """
    Compute circumference by summing distances around a vertex loop.

    Args:
        vertices: (N, 3) array of mesh vertices
        loop_indices: List of vertex indices forming a closed loop

    Returns:
        Circumference in same units as vertices
    """
    total = 0.0
    for i in range(len(loop_indices)):
        v1 = vertices[loop_indices[i]]
        v2 = vertices[loop_indices[(i + 1) % len(loop_indices)]]
        total += compute_distance(v1, v2)
    return total


def compute_geodesic_distance(
    vertices: np.ndarray,
    start_idx: int,
    end_idx: int,
    via_indices: Optional[list] = None
) -> float:
    """
    Approximate geodesic distance along mesh surface.

    For simplicity, we trace through intermediate landmarks.
    """
    if via_indices is None:
        return compute_distance(vertices[start_idx], vertices[end_idx])

    total = 0.0
    path = [start_idx] + via_indices + [end_idx]
    for i in range(len(path) - 1):
        total += compute_distance(vertices[path[i]], vertices[path[i + 1]])
    return total


def classify_body_type(bust: float, waist: float, hips: float) -> BodyType:
    """
    Classify body type based on measurements.

    Uses standard fashion industry definitions.
    """
    bust_hip_ratio = bust / hips if hips > 0 else 1.0
    waist_bust_ratio = waist / bust if bust > 0 else 1.0
    waist_hip_ratio = waist / hips if hips > 0 else 1.0

    # Hourglass: bust ≈ hips, waist significantly smaller
    if (0.9 <= bust_hip_ratio <= 1.1 and waist_bust_ratio < 0.8):
        return BodyType.HOURGLASS

    # Pear: hips notably larger than bust
    if bust_hip_ratio < 0.9:
        return BodyType.PEAR

    # Inverted Triangle: bust notably larger than hips
    if bust_hip_ratio > 1.1:
        return BodyType.INVERTED_TRIANGLE

    # Apple: bust > hips, less defined waist
    if bust_hip_ratio > 1.0 and waist_bust_ratio > 0.8:
        return BodyType.APPLE

    # Rectangle: similar bust, waist, hips
    return BodyType.RECTANGLE


def extract_measurements(
    vertices: np.ndarray,
    scale_factor: float = 100.0,  # Convert to cm (assuming meters input)
    user_height_cm: Optional[float] = None,
) -> BodyMeasurements:
    """
    Extract body measurements from SMPL mesh vertices.

    Args:
        vertices: (6890, 3) SMPL mesh vertices
        scale_factor: Multiplier to convert to cm (default assumes meters)
        user_height_cm: If provided, use to scale measurements

    Returns:
        BodyMeasurements object with all measurements in cm
    """
    # Compute raw measurements (will be in same units as vertices)

    # Circumferences
    bust_raw = compute_circumference(vertices, CIRCUMFERENCE_LOOPS["bust"])
    waist_raw = compute_circumference(vertices, CIRCUMFERENCE_LOOPS["waist"])
    hips_raw = compute_circumference(vertices, CIRCUMFERENCE_LOOPS["hips"])

    # Lengths
    shoulder_width_raw = compute_distance(
        vertices[LANDMARKS["left_shoulder"]],
        vertices[LANDMARKS["right_shoulder"]]
    )

    # Arm length: shoulder -> elbow -> wrist (average of both arms)
    left_arm = (
        compute_distance(
            vertices[LANDMARKS["left_shoulder"]],
            vertices[LANDMARKS["left_elbow"]]
        ) +
        compute_distance(
            vertices[LANDMARKS["left_elbow"]],
            vertices[LANDMARKS["left_wrist"]]
        )
    )
    right_arm = (
        compute_distance(
            vertices[LANDMARKS["right_shoulder"]],
            vertices[LANDMARKS["right_elbow"]]
        ) +
        compute_distance(
            vertices[LANDMARKS["right_elbow"]],
            vertices[LANDMARKS["right_wrist"]]
        )
    )
    arm_length_raw = (left_arm + right_arm) / 2

    # Torso length: shoulder to waist
    torso_raw = compute_distance(
        vertices[LANDMARKS["neck_base"]],
        vertices[LANDMARKS["waist_front"]]
    )

    # Inseam: crotch to ankle (average of both legs)
    left_inseam = compute_distance(
        vertices[LANDMARKS["crotch"]],
        vertices[LANDMARKS["left_ankle"]]
    )
    right_inseam = compute_distance(
        vertices[LANDMARKS["crotch"]],
        vertices[LANDMARKS["right_ankle"]]
    )
    inseam_raw = (left_inseam + right_inseam) / 2

    # Height estimate: head top to heel
    height_raw = compute_distance(
        vertices[LANDMARKS["head_top"]],
        vertices[LANDMARKS["left_heel"]]
    )

    # Determine scale factor
    if user_height_cm is not None and height_raw > 0:
        # Use user-provided height to calibrate
        actual_scale = user_height_cm / height_raw
    else:
        actual_scale = scale_factor

    # Apply scaling to get measurements in cm
    bust = bust_raw * actual_scale
    waist = waist_raw * actual_scale
    hips = hips_raw * actual_scale
    shoulder_width = shoulder_width_raw * actual_scale
    arm_length = arm_length_raw * actual_scale
    torso_length = torso_raw * actual_scale
    inseam = inseam_raw * actual_scale
    height_estimate = height_raw * actual_scale

    # Classify body type
    body_type = classify_body_type(bust, waist, hips)

    # Confidence based on whether we had user height
    confidence = 0.85 if user_height_cm else 0.65

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
