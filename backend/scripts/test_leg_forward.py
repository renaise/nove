#!/usr/bin/env python3
"""
Empirical test: Bring one leg forward (asymmetric stance).
Tests rotation axes and directions for walking/stepping poses.
"""

import numpy as np
import torch
import trimesh
from scipy.spatial.transform import Rotation

from anny import create_fullbody_model


def rotation_matrix_from_axis_angle(axis: str, degrees: float) -> np.ndarray:
    """Create a 4x4 rotation matrix from axis and angle."""
    rad = np.radians(degrees)
    if axis == "x":
        rotvec = np.array([rad, 0, 0])
    elif axis == "y":
        rotvec = np.array([0, rad, 0])
    elif axis == "z":
        rotvec = np.array([0, 0, rad])
    else:
        raise ValueError(f"Unknown axis: {axis}")
    
    rot3x3 = Rotation.from_rotvec(rotvec).as_matrix()
    rot4x4 = np.eye(4)
    rot4x4[:3, :3] = rot3x3
    return rot4x4


def test_leg_forward(axis: str, left_degrees: float, right_degrees: float, output_name: str):
    """Test bringing legs forward/backward."""
    print(f"\n=== Testing {output_name} ===")
    print(f"Left leg: {axis.upper()} rotation {left_degrees}°")
    print(f"Right leg: {axis.upper()} rotation {right_degrees}°")
    
    # Create model
    model = create_fullbody_model(
        rig="default",
        topology="default",
        remove_unattached_vertices=True,
        triangulate_faces=True,
    )
    model = model.to(device="cpu", dtype=torch.float32)
    
    # Get bone info
    bone_labels = model.bone_labels
    num_bones = len(bone_labels)
    
    # Find leg bone indices
    left_upper_idx = bone_labels.index("upperleg01.L")
    right_upper_idx = bone_labels.index("upperleg01.R")
    
    print(f"upperleg01.L index: {left_upper_idx}")
    print(f"upperleg01.R index: {right_upper_idx}")
    
    # Create pose parameters (identity for all bones)
    pose_params = torch.eye(4).unsqueeze(0).unsqueeze(0).repeat(1, num_bones, 1, 1)
    
    # Apply rotations
    left_rot = rotation_matrix_from_axis_angle(axis, left_degrees)
    right_rot = rotation_matrix_from_axis_angle(axis, right_degrees)
    
    pose_params[0, left_upper_idx] = torch.from_numpy(left_rot).float()
    pose_params[0, right_upper_idx] = torch.from_numpy(right_rot).float()
    
    # Generate mesh with pose
    phenotypes = {
        "gender": torch.tensor([[1.0]]),  # female
        "age": torch.tensor([[0.5]]),
        "height": torch.tensor([[0.5]]),
        "weight": torch.tensor([[0.5]]),
        "muscle": torch.tensor([[0.5]]),
        "proportions": torch.tensor([[0.5]]),
    }
    
    output = model(
        pose_parameters=pose_params,
        phenotype_kwargs=phenotypes,
        pose_parameterization="rest_relative",
    )
    
    vertices = output["vertices"][0].detach().cpu().numpy()
    faces = model.get_triangular_faces().cpu().numpy()
    
    # Save mesh
    mesh = trimesh.Trimesh(vertices=vertices, faces=faces, process=False)
    output_path = f"/Users/jonathan/projects/wedding-app/backend/{output_name}.ply"
    mesh.export(output_path)
    print(f"Saved: {output_path}")


if __name__ == "__main__":
    # Test 1: X-axis rotation (forward/backward tilt)
    # Positive X = ? Negative X = ?
    test_leg_forward("x", left_degrees=20, right_degrees=0, output_name="leg_left_x_pos20")
    test_leg_forward("x", left_degrees=-20, right_degrees=0, output_name="leg_left_x_neg20")
    
    # Test 2: Y-axis rotation (twist)
    test_leg_forward("y", left_degrees=20, right_degrees=0, output_name="leg_left_y_pos20")
    test_leg_forward("y", left_degrees=-20, right_degrees=0, output_name="leg_left_y_neg20")
    
    # Test 3: Asymmetric - one forward, one back
    test_leg_forward("x", left_degrees=15, right_degrees=-15, output_name="leg_asymmetric_x15")
    
    print("\n=== Done! Open meshes in Blender to see results ===")
