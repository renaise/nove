#!/usr/bin/env python3
"""
Body measurement extraction using ANNY parametric model.

This script fits ANNY phenotype parameters to a SAM-3D mesh and extracts
semantic body measurements (bust, waist, hips).

Usage:
    python scripts/test_anny_fitting.py <mesh.ply> [height] [gender]

Examples:
    python scripts/test_anny_fitting.py mesh.ply 153cm female
    python scripts/test_anny_fitting.py mesh.ply "5'0" f
    python scripts/test_anny_fitting.py mesh.ply 1.53m male
"""

import sys
from pathlib import Path

import numpy as np
import trimesh

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from services.anny_integration import ANNYBodyAnalyzer


def parse_height(height_str: str) -> float | None:
    """Parse height string (e.g., '5ft 9in', '175cm', '5\\'9\"') to cm."""
    import re

    height_str = height_str.lower().strip()
    try:
        if "cm" in height_str:
            return float(height_str.replace("cm", "").strip())
        elif "m" in height_str and "cm" not in height_str and "'" not in height_str:
            return float(height_str.replace("m", "").strip()) * 100
        else:
            # Assume feet/inches
            match = re.match(
                r"(\d+)'?\s*(\d+)?",
                height_str.replace("ft", "").replace("in", "").replace('"', ""),
            )
            if match:
                feet = float(match.group(1))
                inches = float(match.group(2)) if match.group(2) else 0
                return (feet * 12 + inches) * 2.54
    except Exception:
        pass
    return None


def calculate_bridal_size(bust: float, waist: float, hips: float) -> int:
    """Calculate US bridal size from measurements in inches."""
    SIZE_CHART = [
        (0, 32.5, 24.5, 35.5),
        (2, 33.5, 25.5, 36.5),
        (4, 34.5, 26.5, 37.5),
        (6, 35.5, 27.5, 38.5),
        (8, 36.5, 28.5, 39.5),
        (10, 37.5, 29.5, 40.5),
        (12, 39.0, 31.0, 42.0),
        (14, 41.0, 33.0, 44.0),
        (16, 43.0, 35.0, 46.0),
        (18, 45.0, 37.0, 48.0),
        (20, 47.0, 39.0, 50.0),
    ]

    for size, b, w, h in SIZE_CHART:
        if bust <= b and waist <= w and hips <= h:
            return size
    return 20


def classify_body_type(bust: float, waist: float, hips: float) -> str:
    """Classify body type from measurements in inches."""
    bust_hip_diff = abs(bust - hips)
    waist_diff = min(bust, hips) - waist

    if bust_hip_diff <= 1 and waist_diff >= 9:
        return "hourglass"
    elif hips > bust + 3:
        return "pear"
    elif waist >= hips - 2:
        return "apple"
    elif bust > hips + 3:
        return "inverted_triangle"
    else:
        return "rectangle"


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/test_anny_fitting.py <mesh.ply> [measurements.json] [height] [gender]")
        print()
        print("Examples:")
        print("  python scripts/test_anny_fitting.py mesh.ply 153cm")
        print("  python scripts/test_anny_fitting.py mesh.ply measurements.json 175cm female")
        sys.exit(1)

    ply_path = Path(sys.argv[1])
    if not ply_path.exists():
        print(f"Error: File not found: {ply_path}")
        sys.exit(1)

    # Parse measurements.json if provided
    keypoints_3d = None
    for arg in sys.argv[2:]:
        if arg.endswith('.json'):
            json_path = Path(arg)
            if json_path.exists():
                print(f"Loading keypoints from: {json_path}")
                import json
                with open(json_path) as f:
                    data = json.load(f)
                if 'metadata' in data and 'people' in data['metadata'] and len(data['metadata']['people']) > 0:
                    keypoints_3d = data['metadata']['people'][0]['keypoints_3d']
                elif 'keypoints_3d' in data:
                    keypoints_3d = data['keypoints_3d']
                break

    # Parse optional height argument
    user_height_cm = None
    for arg in sys.argv[2:]:
        if arg.endswith('.json'): continue
        parsed = parse_height(arg)
        if parsed:
            user_height_cm = parsed
            print(f"User provided height: {arg} -> {user_height_cm:.1f} cm")
            break

    # Parse optional gender argument
    user_gender = None
    for arg in sys.argv[2:]:
        if arg.lower() in ("male", "m"):
            user_gender = "male"
            print(f"User provided gender: male")
        elif arg.lower() in ("female", "f"):
            user_gender = "female"
            print(f"User provided gender: female")

    print(f"\nLoading mesh: {ply_path}")
    mesh = trimesh.load(str(ply_path))
    vertices = np.array(mesh.vertices, dtype=np.float32)
    faces = np.array(mesh.faces, dtype=np.int32) if hasattr(mesh, 'faces') and mesh.faces is not None else None
    print(f"Vertices: {len(vertices)}")
    print(f"Faces: {len(faces) if faces is not None else 'None'}")

    # Get mesh bounds
    print(f"Mesh bounds:")
    print(f"  X: [{vertices[:,0].min():.3f}, {vertices[:,0].max():.3f}]")
    print(f"  Y: [{vertices[:,1].min():.3f}, {vertices[:,1].max():.3f}]")
    print(f"  Z: [{vertices[:,2].min():.3f}, {vertices[:,2].max():.3f}]")

    mesh_height = vertices[:, 1].max() - vertices[:, 1].min()
    print(f"  Height (Y): {mesh_height:.3f}m = {mesh_height * 100:.1f}cm")

    print("\n" + "=" * 50)
    print("FITTING ANNY MODEL")
    print("=" * 50)

    # Create analyzer and fit
    analyzer = ANNYBodyAnalyzer(device="cpu")

    # Save debug meshes next to input file
    debug_prefix = str(ply_path.parent / "debug")

    result = analyzer.analyze_from_vertices(
        vertices,
        user_height_cm=user_height_cm,
        user_gender=user_gender,
        keypoints_3d=keypoints_3d,
        faces=faces,
        save_debug_meshes=debug_prefix,
    )

    print("\n" + "=" * 50)
    print("RESULTS")
    print("=" * 50)

    m = result.measurements
    bust_in = m.bust_cm / 2.54
    waist_in = m.waist_cm / 2.54
    hip_in = m.hips_cm / 2.54

    print(f"\n  Height: {m.height_cm:.1f} cm / {m.height_cm / 2.54:.1f} in")
    print(f"  Bust:   {m.bust_cm:.1f} cm / {bust_in:.1f} in")
    print(f"  Waist:  {m.waist_cm:.1f} cm / {waist_in:.1f} in")
    print(f"  Hips:   {m.hips_cm:.1f} cm / {hip_in:.1f} in")
    print(f"  Weight: {m.weight_kg:.1f} kg / {m.weight_kg * 2.205:.1f} lbs")
    print(f"  BMI:    {m.bmi:.1f}")

    size = calculate_bridal_size(bust_in, waist_in, hip_in)
    body_type = classify_body_type(bust_in, waist_in, hip_in)

    print(f"\n  Estimated Bridal Size: {size}")
    print(f"  Body Type: {body_type}")
    print(f"  Confidence: {result.confidence:.0%}")

    print("\n  Fitted Phenotypes:")
    for k, v in result.phenotypes.items():
        print(f"    {k}: {v:.3f}")

    print("\n" + "=" * 50)


if __name__ == "__main__":
    main()
