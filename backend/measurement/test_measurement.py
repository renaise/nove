#!/usr/bin/env python3
"""
Test script for the body measurement service.

Usage:
    python test_measurement.py [image_path] [--height HEIGHT_CM]

If no image is provided, creates a synthetic test.
"""

import argparse
import sys
from pathlib import Path

import numpy as np


def test_anthropometry():
    """Test the anthropometry module with synthetic SMPL vertices."""
    print("\n" + "=" * 60)
    print("Testing Anthropometry Module")
    print("=" * 60)

    from src.measurement.anthropometry import extract_measurements

    # Create synthetic SMPL-like vertices (simplified)
    # Real SMPL has 6890 vertices, we'll create a minimal set for testing
    np.random.seed(42)

    # Create a basic humanoid shape
    n_vertices = 6890
    vertices = np.zeros((n_vertices, 3))

    # Set approximate body proportions (in meters, ~1.7m tall person)
    # Head at top
    vertices[411] = [0, 1.7, 0]  # head_top

    # Shoulders
    vertices[5431] = [-0.2, 1.4, 0]  # left_shoulder
    vertices[1860] = [0.2, 1.4, 0]  # right_shoulder

    # Neck
    vertices[3068] = [0, 1.45, 0]  # neck_base

    # Bust points (form a rough circle)
    vertices[1424] = [-0.15, 1.25, 0.1]  # left_bust
    vertices[4904] = [0.15, 1.25, 0.1]  # right_bust
    vertices[3042] = [0, 1.25, 0.15]  # bust_front
    vertices[3158] = [0, 1.25, -0.1]  # bust_back

    # Waist points
    vertices[3500] = [0, 1.05, 0.12]  # waist_front
    vertices[3022] = [0, 1.05, -0.08]  # waist_back
    vertices[937] = [-0.13, 1.05, 0]  # waist_left
    vertices[4418] = [0.13, 1.05, 0]  # waist_right

    # Hip points
    vertices[3149] = [0, 0.9, 0.14]  # hip_front
    vertices[3119] = [0, 0.9, -0.1]  # hip_back
    vertices[856] = [-0.17, 0.9, 0]  # hip_left
    vertices[4343] = [0.17, 0.9, 0]  # hip_right

    # Arms
    vertices[5325] = [-0.35, 1.2, 0]  # left_elbow
    vertices[1740] = [0.35, 1.2, 0]  # right_elbow
    vertices[5559] = [-0.5, 1.0, 0]  # left_wrist
    vertices[2094] = [0.5, 1.0, 0]  # right_wrist

    # Legs
    vertices[1009] = [-0.1, 0.5, 0]  # left_knee
    vertices[4505] = [0.1, 0.5, 0]  # right_knee
    vertices[3327] = [-0.1, 0.08, 0]  # left_ankle
    vertices[6728] = [0.1, 0.08, 0]  # right_ankle
    vertices[3387] = [-0.1, 0, 0]  # left_heel
    vertices[6787] = [0.1, 0, 0]  # right_heel

    # Fill in circumference loops with interpolated values
    # Bust loop
    bust_loop = [3042, 2989, 2964, 1227, 1231, 1319, 1320, 1424, 1302, 1303,
                 689, 692, 3049, 3043, 3044, 3050, 4127, 4131, 4767, 4768,
                 4904, 4781, 4780, 4168, 4169, 3158, 3157, 3156, 3042]

    # Create circular bust points
    for i, idx in enumerate(bust_loop):
        angle = 2 * np.pi * i / len(bust_loop)
        vertices[idx] = [
            0.15 * np.sin(angle),  # x
            1.25,  # y (bust height)
            0.12 * np.cos(angle),  # z
        ]

    # Waist loop
    waist_loop = [3500, 3502, 1337, 1338, 1339, 937, 938, 939, 3021, 3022,
                  3023, 3024, 4420, 4419, 4418, 4821, 4820, 4819, 3503, 3500]

    for i, idx in enumerate(waist_loop):
        angle = 2 * np.pi * i / len(waist_loop)
        vertices[idx] = [
            0.12 * np.sin(angle),  # x
            1.05,  # y (waist height)
            0.10 * np.cos(angle),  # z
        ]

    # Hip loop
    hip_loop = [3149, 3148, 892, 891, 890, 889, 856, 855, 854, 3119,
                3118, 4343, 4342, 4378, 4377, 4376, 4375, 3150, 3149]

    for i, idx in enumerate(hip_loop):
        angle = 2 * np.pi * i / len(hip_loop)
        vertices[idx] = [
            0.16 * np.sin(angle),  # x
            0.9,  # y (hip height)
            0.13 * np.cos(angle),  # z
        ]

    # Test without user height
    print("\nTest 1: Without user height (relative measurements)")
    measurements = extract_measurements(vertices, scale_factor=100.0)
    print(f"  Bust: {measurements.bust:.1f} cm")
    print(f"  Waist: {measurements.waist:.1f} cm")
    print(f"  Hips: {measurements.hips:.1f} cm")
    print(f"  Body Type: {measurements.body_type.value}")
    print(f"  Confidence: {measurements.confidence:.0%}")

    # Test with user height
    print("\nTest 2: With user height (170 cm)")
    measurements = extract_measurements(vertices, user_height_cm=170.0)
    print(f"  Bust: {measurements.bust:.1f} cm")
    print(f"  Waist: {measurements.waist:.1f} cm")
    print(f"  Hips: {measurements.hips:.1f} cm")
    print(f"  Shoulder Width: {measurements.shoulder_width:.1f} cm")
    print(f"  Arm Length: {measurements.arm_length:.1f} cm")
    print(f"  Body Type: {measurements.body_type.value}")
    print(f"  Confidence: {measurements.confidence:.0%}")

    # Test bridal sizing
    print("\nBridal Size Recommendation:")
    bridal = measurements.get_bridal_size()
    print(f"  Recommended Size: {bridal['recommended_size']}")
    print(f"  Size Range: {bridal['size_range']}")

    print("\n✓ Anthropometry module tests passed!")
    return True


def test_hmr_model():
    """Test the HMR model loading."""
    print("\n" + "=" * 60)
    print("Testing HMR Model Loading")
    print("=" * 60)

    try:
        from src.measurement.hmr import load_model, get_device

        print(f"\nDevice: {get_device()}")
        print("Loading model (this may take a moment on first run)...")

        model = load_model()
        print(f"✓ Model loaded successfully!")
        print(f"  - Backbone: ViT-H/16")
        print(f"  - Feature dim: {model.feat_dim}")
        print(f"  - Device: {model.device}")

        return model
    except Exception as e:
        print(f"✗ Model loading failed: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_full_pipeline(image_path: str, height_cm: float = None):
    """Test the full measurement pipeline with a real image."""
    print("\n" + "=" * 60)
    print("Testing Full Pipeline")
    print("=" * 60)

    from PIL import Image
    from src.measurement.service import measure

    print(f"\nImage: {image_path}")
    print(f"Height: {height_cm} cm" if height_cm else "Height: not provided")

    # Load and display image info
    img = Image.open(image_path)
    print(f"Image size: {img.size}")

    print("\nProcessing...")
    measurements = measure(image_path, user_height_cm=height_cm)

    print("\n" + "-" * 40)
    print("MEASUREMENTS")
    print("-" * 40)
    for key, value in measurements.to_dict().items():
        print(f"  {key}: {value}")

    print("\n" + "-" * 40)
    print("BRIDAL SIZE")
    print("-" * 40)
    bridal = measurements.get_bridal_size()
    for key, value in bridal.items():
        print(f"  {key}: {value}")

    print("\n✓ Full pipeline test completed!")
    return measurements


def main():
    parser = argparse.ArgumentParser(description="Test body measurement service")
    parser.add_argument("image", nargs="?", help="Path to test image")
    parser.add_argument("--height", type=float, help="User height in cm")
    parser.add_argument("--skip-model", action="store_true",
                       help="Skip model loading test")

    args = parser.parse_args()

    print("=" * 60)
    print("NOVIA BODY MEASUREMENT SERVICE - TEST SUITE")
    print("=" * 60)

    # Test 1: Anthropometry module
    test_anthropometry()

    # Test 2: Model loading (optional)
    if not args.skip_model:
        model = test_hmr_model()
    else:
        print("\n[Skipping model loading test]")

    # Test 3: Full pipeline with image (if provided)
    if args.image:
        if not Path(args.image).exists():
            print(f"\n✗ Image not found: {args.image}")
            return 1

        test_full_pipeline(args.image, args.height)

    print("\n" + "=" * 60)
    print("ALL TESTS COMPLETED")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
