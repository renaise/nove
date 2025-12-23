#!/usr/bin/env python3
"""
Load SAM-3D joints from measurements.json instead of extracting from mesh.

SAM-3D keypoints_3d format (70 keypoints):
- 0: nose/head
- 1-2: left_eye, right_eye
- 3-4: left_ear, right_ear
- 5-6: left_shoulder, right_shoulder
- 7-8: left_elbow, right_elbow
- 9-10: left_hip, right_hip
- 11-12: left_knee, right_knee
- 13-14: left_ankle, right_ankle
- 15-20: foot keypoints
- 21-41: left hand (21 joints, index 21 is wrist)
- 42-62: right hand points on torso/arm (index 63+ seem to be wrist area)
- 63-69: additional body landmarks

Coordinate system:
- X: left/right (+X = right side of body in image)
- Y: up/down (more negative = higher, -1.5 is head, 0 is feet)
- Z: front/back
"""

import json
import numpy as np
from pathlib import Path


# Mapping from SAM-3D keypoint indices to our joint names
SAM3D_JOINT_MAP = {
    'head': 0,
    'shoulder_l': 6,   # Note: SAM-3D left = negative X
    'shoulder_r': 5,   # SAM-3D right = positive X
    'elbow_l': 8,
    'elbow_r': 7,
    'hip_l': 10,
    'hip_r': 9,
    'knee_l': 12,
    'knee_r': 11,
    'ankle_l': 14,
    'ankle_r': 13,
    'wrist_l': 21,     # First joint of left hand cluster
    # wrist_r is tricky - need to find in the hand cluster
}


def load_sam3d_joints(json_path: str) -> dict[str, np.ndarray]:
    """
    Load 3D joint positions from SAM-3D measurements.json.

    Args:
        json_path: Path to measurements.json from SAM-3D

    Returns:
        Dictionary mapping joint names to 3D positions in ANNY coordinates
        (X-flipped so +X = left, matching ANNY convention)
    """
    with open(json_path) as f:
        data = json.load(f)

    kp = data['metadata']['people'][0]['keypoints_3d']

    joints = {}

    for joint_name, idx in SAM3D_JOINT_MAP.items():
        if idx < len(kp):
            pos = np.array(kp[idx])
            # Flip X to match ANNY coordinate system (+X = left)
            pos[0] = -pos[0]
            joints[joint_name] = pos

    # Find right wrist by looking for the right hand cluster
    # Right hand cluster starts around index 63 based on X position
    for idx in [63, 64, 65]:
        if idx < len(kp):
            pos = np.array(kp[idx])
            if pos[0] > 0:  # Positive X = right side in SAM-3D
                joints['wrist_r'] = np.array([-pos[0], pos[1], pos[2]])
                break

    # Add pelvis as midpoint of hips
    if 'hip_l' in joints and 'hip_r' in joints:
        joints['pelvis'] = (joints['hip_l'] + joints['hip_r']) / 2

    # Add neck as midpoint of shoulders, slightly higher
    if 'shoulder_l' in joints and 'shoulder_r' in joints:
        neck = (joints['shoulder_l'] + joints['shoulder_r']) / 2
        # Neck is slightly higher than shoulders (more negative Y)
        neck[1] -= 0.05
        joints['neck'] = neck

    return joints


def print_joints(joints: dict[str, np.ndarray]):
    """Print joint positions in a table."""
    print(f"{'Joint':<15} {'X':>10} {'Y':>10} {'Z':>10}")
    print("-" * 50)
    for name in sorted(joints.keys()):
        pos = joints[name]
        print(f"{name:<15} {pos[0]:>+10.4f} {pos[1]:>+10.4f} {pos[2]:>+10.4f}")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Load SAM-3D joints from JSON")
    parser.add_argument("json_path", type=str, help="Path to measurements.json")
    args = parser.parse_args()

    joints = load_sam3d_joints(args.json_path)
    print(f"\nLoaded {len(joints)} joints from SAM-3D:\n")
    print_joints(joints)

    # Show coordinate system info
    print("\n=== Coordinate Analysis ===")
    if 'head' in joints and 'ankle_l' in joints:
        height = joints['head'][1] - joints['ankle_l'][1]
        print(f"Height (head to ankle Y): {abs(height):.3f} units")

    if 'shoulder_l' in joints and 'shoulder_r' in joints:
        width = abs(joints['shoulder_l'][0] - joints['shoulder_r'][0])
        print(f"Shoulder width (X): {width:.3f} units")


if __name__ == "__main__":
    main()
