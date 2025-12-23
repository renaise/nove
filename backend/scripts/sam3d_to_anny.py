#!/usr/bin/env python3
"""
SAM-3D to ANNY Pose Matching

Takes a SAM-3D mesh, extracts joints, and drives ANNY to match the pose.

Usage:
    python sam3d_to_anny.py <sam3d_mesh.ply> [--height HEIGHT_CM] [--gender female|male]

This will:
1. Scale SAM-3D mesh to user height
2. Extract joint positions
3. Compute bone rotations to match joints
4. Generate posed ANNY mesh
"""

import argparse
import numpy as np
import torch
import trimesh
from scipy.spatial.transform import Rotation
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from services.anny_integration import ANNYBodyAnalyzer


def load_joints_from_ply(path: str) -> dict[str, np.ndarray]:
    """Load joint positions from a debug joints PLY file.

    Looks for _points.ply version first (simple point cloud with one vertex per joint),
    falls back to sphere mesh and computes centroids of connected components.
    """
    # Try loading _points.ply first (simple format)
    points_path = path.replace('.ply', '_points.ply')
    if Path(points_path).exists():
        mesh = trimesh.load(points_path)
        vertices = np.array(mesh.vertices)
    else:
        # Fallback: load sphere mesh and compute centroids
        mesh = trimesh.load(path)
        if hasattr(mesh, 'split'):
            # Split into connected components (each sphere is one component)
            components = mesh.split()
            vertices = np.array([c.centroid for c in components])
        else:
            vertices = np.array(mesh.vertices)

    # Standard joint order (must match _save_joints_debug)
    joint_names = [
        'pelvis', 'hip_l', 'hip_r', 'knee_l', 'knee_r',
        'ankle_l', 'ankle_r', 'shoulder_l', 'shoulder_r',
        'elbow_l', 'elbow_r', 'wrist_l', 'wrist_r',
        'neck', 'head'
    ]

    joints = {}
    for i, name in enumerate(joint_names):
        if i < len(vertices):
            pos = vertices[i]
            # Skip NaN entries (missing joints)
            if not np.any(np.isnan(pos)):
                joints[name] = pos

    return joints


def print_joints(joints: dict[str, np.ndarray], title: str = "Joints"):
    """Print joint positions in a table."""
    print(f"\n=== {title} ===")
    print(f"{'Joint':<15} {'X':>10} {'Y':>10} {'Z':>10}")
    print("-" * 50)
    for name, pos in sorted(joints.items()):
        print(f"{name:<15} {pos[0]:>10.4f} {pos[1]:>10.4f} {pos[2]:>10.4f}")


def compute_direction(joints: dict, from_joint: str, to_joint: str) -> np.ndarray:
    """Compute normalized direction vector between two joints."""
    if from_joint not in joints or to_joint not in joints:
        return None
    direction = joints[to_joint] - joints[from_joint]
    length = np.linalg.norm(direction)
    if length < 1e-6:
        return None
    return direction / length


def compute_angle_between(v1: np.ndarray, v2: np.ndarray) -> float:
    """Compute angle in degrees between two vectors."""
    v1 = v1 / (np.linalg.norm(v1) + 1e-8)
    v2 = v2 / (np.linalg.norm(v2) + 1e-8)
    dot = np.clip(np.dot(v1, v2), -1, 1)
    return np.degrees(np.arccos(dot))


def analyze_pose(joints: dict):
    """Analyze the pose from joint positions."""
    print("\n=== Pose Analysis ===")

    # Leg analysis
    for side, prefix in [('Left', 'l'), ('Right', 'r')]:
        hip_to_knee = compute_direction(joints, f'hip_{prefix}', f'knee_{prefix}')
        knee_to_ankle = compute_direction(joints, f'knee_{prefix}', f'ankle_{prefix}')

        if hip_to_knee is not None and knee_to_ankle is not None:
            knee_angle = compute_angle_between(hip_to_knee, knee_to_ankle)
            print(f"{side} leg:")
            print(f"  Hip→Knee direction: [{hip_to_knee[0]:.3f}, {hip_to_knee[1]:.3f}, {hip_to_knee[2]:.3f}]")
            print(f"  Knee→Ankle direction: [{knee_to_ankle[0]:.3f}, {knee_to_ankle[1]:.3f}, {knee_to_ankle[2]:.3f}]")
            print(f"  Knee bend angle: {180 - knee_angle:.1f}° (180° = straight)")

    # Arm analysis
    for side, prefix in [('Left', 'l'), ('Right', 'r')]:
        shoulder_to_elbow = compute_direction(joints, f'shoulder_{prefix}', f'elbow_{prefix}')
        elbow_to_wrist = compute_direction(joints, f'elbow_{prefix}', f'wrist_{prefix}')

        if shoulder_to_elbow is not None and elbow_to_wrist is not None:
            elbow_angle = compute_angle_between(shoulder_to_elbow, elbow_to_wrist)
            print(f"{side} arm:")
            print(f"  Shoulder→Elbow direction: [{shoulder_to_elbow[0]:.3f}, {shoulder_to_elbow[1]:.3f}, {shoulder_to_elbow[2]:.3f}]")
            print(f"  Elbow→Wrist direction: [{elbow_to_wrist[0]:.3f}, {elbow_to_wrist[1]:.3f}, {elbow_to_wrist[2]:.3f}]")
            print(f"  Elbow bend angle: {180 - elbow_angle:.1f}° (180° = straight)")


def run_pipeline(mesh_path: str, height_cm: float = 165.0, gender: str = "female"):
    """Run the full pipeline: SAM-3D → joints → ANNY pose."""

    print(f"Loading SAM-3D mesh: {mesh_path}")
    print(f"User height: {height_cm}cm, gender: {gender}")

    # Initialize ANNY integration
    anny = ANNYBodyAnalyzer()

    # Load mesh
    sam3d_mesh = trimesh.load(mesh_path)
    vertices = np.array(sam3d_mesh.vertices)
    faces = np.array(sam3d_mesh.faces) if hasattr(sam3d_mesh, 'faces') else None
    print(f"Mesh vertices: {len(vertices)}")

    # Run the pipeline with debug output
    result = anny.analyze_from_vertices(
        vertices=vertices,
        user_height_cm=height_cm,
        user_gender=gender,
        faces=faces,
        save_debug_meshes="debug"
    )

    print(f"\n=== Results ===")
    print(f"Bust: {result.measurements.bust_cm:.1f} cm")
    print(f"Waist: {result.measurements.waist_cm:.1f} cm")
    print(f"Hips: {result.measurements.hips_cm:.1f} cm")

    # Load and compare joints
    print("\n" + "="*80)
    print("JOINT COMPARISON")
    print("="*80)

    sam3d_aligned = None
    anny_posed = None

    if Path("debug_sam3d_joints_aligned.ply").exists():
        sam3d_aligned = load_joints_from_ply("debug_sam3d_joints_aligned.ply")
        print_joints(sam3d_aligned, "SAM-3D Joints (X-flipped to ANNY coords)")

    if Path("debug_anny_posed_joints.ply").exists():
        anny_posed = load_joints_from_ply("debug_anny_posed_joints.ply")
        print_joints(anny_posed, "ANNY Posed Joints (after bone rotations)")

    # Side-by-side comparison
    if sam3d_aligned and anny_posed:
        # First, compute pelvis alignment offset
        if 'pelvis' in sam3d_aligned and 'pelvis' in anny_posed:
            pelvis_offset = sam3d_aligned['pelvis'] - anny_posed['pelvis']
            print(f"\n=== PELVIS ALIGNMENT ===")
            print(f"SAM-3D pelvis: [{sam3d_aligned['pelvis'][0]:+.4f}, {sam3d_aligned['pelvis'][1]:+.4f}, {sam3d_aligned['pelvis'][2]:+.4f}]")
            print(f"ANNY pelvis:   [{anny_posed['pelvis'][0]:+.4f}, {anny_posed['pelvis'][1]:+.4f}, {anny_posed['pelvis'][2]:+.4f}]")
            print(f"Offset needed: [{pelvis_offset[0]:+.4f}, {pelvis_offset[1]:+.4f}, {pelvis_offset[2]:+.4f}]")
        else:
            pelvis_offset = np.zeros(3)

        print("\n=== JOINT POSITION ERRORS (after pelvis alignment) ===")
        print(f"{'Joint':<15} {'dX':>10} {'dY':>10} {'dZ':>10} {'dist':>10}")
        print("-" * 60)

        total_error = 0
        count = 0
        for name in sorted(sam3d_aligned.keys()):
            if name in anny_posed:
                sam_pos = sam3d_aligned[name]
                # Align ANNY by adding pelvis offset
                anny_pos = anny_posed[name] + pelvis_offset
                diff = sam_pos - anny_pos
                dist = np.linalg.norm(diff)
                total_error += dist
                count += 1
                print(f"{name:<15} {diff[0]:>+10.4f} {diff[1]:>+10.4f} {diff[2]:>+10.4f} {dist:>10.4f}")

        if count > 0:
            print(f"\nMean joint error (after pelvis alignment): {total_error/count:.4f} m ({total_error/count*100:.1f} cm)")

    # Analyze SAM-3D pose
    if sam3d_aligned:
        analyze_pose(sam3d_aligned)

    print("\n=== Debug files saved ===")
    print("  debug_sam3d_scaled.ply - SAM-3D mesh scaled to user height")
    print("  debug_sam3d_joints.ply - Extracted joints from SAM-3D (original coords)")
    print("  debug_sam3d_joints_aligned.ply - Joints X-flipped to ANNY coordinate space")
    print("  debug_anny_posed_joints.ply - ANNY joints after applying computed rotations")
    print("  debug_anny_fitted.ply - ANNY mesh with fitted phenotypes (T-pose)")


def main():
    parser = argparse.ArgumentParser(description="SAM-3D to ANNY pose matching")
    parser.add_argument("mesh", type=str, help="Path to SAM-3D mesh PLY file")
    parser.add_argument("--height", type=float, default=165.0, help="User height in cm")
    parser.add_argument("--gender", type=str, default="female", choices=["female", "male"])
    args = parser.parse_args()

    run_pipeline(args.mesh, args.height, args.gender)


if __name__ == "__main__":
    main()
