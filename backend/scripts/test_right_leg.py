#!/usr/bin/env python3
"""
Empirical test: Right leg forward/backward to check if inverted from left.
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


def test_right_leg(axis: str, degrees: float, output_name: str):
    """Test right leg rotation."""
    print(f"\n=== Testing {output_name} ===")
    print(f"Right leg: {axis.upper()} rotation {degrees}°")
    
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
    right_upper_idx = bone_labels.index("upperleg01.R")
    
    # Create pose parameters (identity for all bones)
    pose_params = torch.eye(4).unsqueeze(0).unsqueeze(0).repeat(1, num_bones, 1, 1)
    
    # Apply rotation to right leg only
    right_rot = rotation_matrix_from_axis_angle(axis, degrees)
    pose_params[0, right_upper_idx] = torch.from_numpy(right_rot).float()
    
    # Generate mesh with pose
    phenotypes = {
        "gender": torch.tensor([[1.0]]),
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
    # Test X-axis (forward/backward)
    test_right_leg("x", degrees=20, output_name="leg_right_x_pos20")
    test_right_leg("x", degrees=-20, output_name="leg_right_x_neg20")
    
    # Test Y-axis (inward/outward rotation)
    test_right_leg("y", degrees=20, output_name="leg_right_y_pos20")
    test_right_leg("y", degrees=-20, output_name="leg_right_y_neg20")
    
    print("\n=== Done! ===")
    print("Left leg observations:")
    print("  -X = forward, +X = backward")
    print("  -Y = outward, +Y = inward")
    print("\nCheck if right leg is inverted!")
