#!/usr/bin/env python3
"""
Load SAM-3D keypoints from measurements.json and align to mesh.

SAM-3D outputs keypoints in a different coordinate system than the mesh PLY.
This script applies the correct transformation to align them.

Keypoint indices (70 total):
- 0: nose/head
- 1-2: left_eye, right_eye
- 3-4: left_ear, right_ear
- 5: right_shoulder (positive X in SAM-3D)
- 6: left_shoulder (negative X in SAM-3D)
- 7: right_elbow
- 8: left_elbow
- 9: right_hip
- 10: left_hip
- 11: right_knee
- 12: left_knee
- 13: right_ankle
- 14: left_ankle
- 15-20: foot keypoints
- 21-41: left hand (21 is wrist)
- 42-62: torso/chest points
- 63-69: additional landmarks

Coordinate system difference:
- Mesh PLY: Y up (positive = higher), Z depth (around -1.5)
- Keypoints JSON: Y inverted (negative = higher), Z centered around 0

Transform: flip Y sign, then translate to align hip centers.

Usage:
    python load_sam3d_keypoints.py <mesh.ply> <measurements.json> [--output keypoints.ply]
"""

import argparse
import json
import numpy as np
import trimesh
from pathlib import Path


# Mapping from keypoint indices to joint names
KEYPOINT_NAMES = {
    0: 'head',
    5: 'shoulder_r',  # positive X in SAM-3D = right
    6: 'shoulder_l',  # negative X in SAM-3D = left
    7: 'elbow_r',
    8: 'elbow_l',
    9: 'hip_r',
    10: 'hip_l',
    11: 'knee_r',
    12: 'knee_l',
    13: 'ankle_r',
    14: 'ankle_l',
    21: 'wrist_l',  # first joint of left hand cluster
}


def load_and_align_keypoints(
    mesh_path: str,
    json_path: str,
) -> tuple[np.ndarray, dict[str, np.ndarray]]:
    """
    Load keypoints from JSON and align to mesh coordinate system.

    Args:
        mesh_path: Path to SAM-3D mesh PLY file
        json_path: Path to measurements.json with keypoints_3d

    Returns:
        Tuple of (all_keypoints_aligned, named_joints_dict)
    """
    # Load mesh
    mesh = trimesh.load(mesh_path)
    mesh_verts = np.array(mesh.vertices)

    # Load keypoints
    with open(json_path) as f:
        data = json.load(f)
    kp = np.array(data['metadata']['people'][0]['keypoints_3d'])

    # Detect coordinate system of mesh
    # Z-up if Z range is larger than Y range (height is Z in ANNY space)
    z_range = mesh_verts[:, 2].max() - mesh_verts[:, 2].min()
    y_range = mesh_verts[:, 1].max() - mesh_verts[:, 1].min()
    is_anny_space = z_range > y_range

    if is_anny_space:
        print("Detected Z-up mesh (ANNY coordinate system)")
        # SAM-3D JSON -> ANNY space (X, -Z, Y)
        # 1. Flip Y (JSON Y is inverted relative to raw PLY)
        kp_ply_space = kp.copy()
        kp_ply_space[:, 1] *= -1

        # 2. Transform to ANNY space (X, -Z, Y)
        kp_transformed = kp_ply_space[:, [0, 2, 1]].copy()
        kp_transformed[:, 1] *= -1

        # 3. Align with mesh (assume mesh is centered or at least has its own origin)
        # For debug_sam3d_scaled.ply, it's centered at 0
        mesh_center = mesh_verts.mean(axis=0)
        
        # We need to find the scale factor too if the mesh is scaled
        # Estimate scale from height
        kp_height = kp_transformed[:, 2].max() - kp_transformed[:, 2].min()
        scale = z_range / kp_height if kp_height > 0 else 1.0
        print(f"Estimated scale factor: {scale:.4f}")
        
        kp_transformed *= scale
        
        # Center alignment
        kp_center = kp_transformed.mean(axis=0)
        offset = mesh_center - kp_center
        kp_transformed += offset
    else:
        print("Detected Y-up mesh (Raw SAM-3D coordinate system)")
        # Transform keypoints to match mesh coordinate system
        # Step 1: Flip Y (keypoints have inverted Y axis)
        kp_transformed = kp.copy()
        kp_transformed[:, 1] *= -1

        # Step 2: Align using hip centers as anchor
        kp_hip_center = (kp_transformed[9] + kp_transformed[10]) / 2

        # Find mesh hip region (around Y=0)
        hip_y = 0
        hip_mask = np.abs(mesh_verts[:, 1] - hip_y) < 0.1
        if hip_mask.sum() > 0:
            mesh_hip_center = mesh_verts[hip_mask].mean(axis=0)
        else:
            mesh_hip_center = mesh_verts.mean(axis=0)

        # Apply offset
        offset = mesh_hip_center - kp_hip_center
        kp_transformed += offset

    # Extract named joints
    joints = {}
    for idx, name in KEYPOINT_NAMES.items():
        if idx < len(kp_transformed):
            joints[name] = kp_transformed[idx]

    # Add computed joints
    if 'hip_l' in joints and 'hip_r' in joints:
        joints['pelvis'] = (joints['hip_l'] + joints['hip_r']) / 2

    if 'shoulder_l' in joints and 'shoulder_r' in joints:
        joints['neck'] = (joints['shoulder_l'] + joints['shoulder_r']) / 2
        if is_anny_space:
            joints['neck'][2] += 0.05  # higher in Z
        else:
            joints['neck'][1] += 0.05  # higher in Y

    return kp_transformed, joints


def save_keypoints_ply(
    keypoints: np.ndarray,
    output_path: str,
    sphere_radius: float = 0.02,
):
    """Save keypoints as colored spheres for visualization."""
    meshes = []

    # Body joints (0-20) in red/orange gradient
    for i in range(min(21, len(keypoints))):
        sphere = trimesh.creation.icosphere(subdivisions=1, radius=sphere_radius)
        sphere.apply_translation(keypoints[i])
        r, g, b = 255, int(i * 12), 0
        sphere.visual.vertex_colors = np.array(
            [[r, g, b, 255]] * len(sphere.vertices), dtype=np.uint8
        )
        meshes.append(sphere)

    # Left hand (21-41) in blue
    for i in range(21, min(42, len(keypoints))):
        sphere = trimesh.creation.icosphere(subdivisions=1, radius=sphere_radius * 0.5)
        sphere.apply_translation(keypoints[i])
        sphere.visual.vertex_colors = np.array(
            [[0, 100, 255, 255]] * len(sphere.vertices), dtype=np.uint8
        )
        meshes.append(sphere)

    # Torso points (42-62) in green
    for i in range(42, min(63, len(keypoints))):
        sphere = trimesh.creation.icosphere(subdivisions=1, radius=sphere_radius * 0.5)
        sphere.apply_translation(keypoints[i])
        sphere.visual.vertex_colors = np.array(
            [[0, 255, 100, 255]] * len(sphere.vertices), dtype=np.uint8
        )
        meshes.append(sphere)

    # Additional landmarks (63+) in purple
    for i in range(63, len(keypoints)):
        sphere = trimesh.creation.icosphere(subdivisions=1, radius=sphere_radius * 0.75)
        sphere.apply_translation(keypoints[i])
        sphere.visual.vertex_colors = np.array(
            [[200, 0, 255, 255]] * len(sphere.vertices), dtype=np.uint8
        )
        meshes.append(sphere)

    combined = trimesh.util.concatenate(meshes)
    combined.export(output_path)


def print_joints(joints: dict[str, np.ndarray]):
    """Print joint positions."""
    print(f"{'Joint':<15} {'X':>10} {'Y':>10} {'Z':>10}")
    print("-" * 50)
    for name in sorted(joints.keys()):
        pos = joints[name]
        print(f"{name:<15} {pos[0]:>+10.4f} {pos[1]:>+10.4f} {pos[2]:>+10.4f}")


def main():
    parser = argparse.ArgumentParser(
        description="Load SAM-3D keypoints from JSON and align to mesh"
    )
    parser.add_argument("mesh", type=str, help="Path to SAM-3D mesh PLY file")
    parser.add_argument("json", type=str, help="Path to measurements.json")
    parser.add_argument(
        "--output", "-o", type=str, default="sam3d_keypoints_aligned.ply",
        help="Output PLY path for visualization"
    )
    args = parser.parse_args()

    print(f"Loading mesh: {args.mesh}")
    print(f"Loading keypoints: {args.json}")

    keypoints, joints = load_and_align_keypoints(args.mesh, args.json)

    print(f"\nExtracted {len(joints)} named joints:")
    print_joints(joints)

    save_keypoints_ply(keypoints, args.output)
    print(f"\nSaved keypoints visualization: {args.output}")
    print(f"Colors: Red/Orange=body(0-20), Blue=left_hand(21-41), Green=torso(42-62), Purple=extra(63+)")


if __name__ == "__main__":
    main()
