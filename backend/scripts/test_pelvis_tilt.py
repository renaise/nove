#!/usr/bin/env python3
"""
Empirical test: Pelvis tilt (hip drop).
Tests rotation axes and directions for pelvis/root bone.
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


def test_pelvis(axis: str, degrees: float, output_name: str):
    """Test pelvis/root rotation."""
    print(f"\n=== Testing {output_name} ===")
    print(f"Root bone: {axis.upper()} rotation {degrees}°")
    
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
    
    # Find root bone index
    root_idx = bone_labels.index("root")
    print(f"root index: {root_idx}")
    
    # Create pose parameters (identity for all bones)
    pose_params = torch.eye(4).unsqueeze(0).unsqueeze(0).repeat(1, num_bones, 1, 1)
    
    # Apply rotation to root
    root_rot = rotation_matrix_from_axis_angle(axis, degrees)
    pose_params[0, root_idx] = torch.from_numpy(root_rot).float()
    
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
    # Test all three axes at 15 degrees
    test_pelvis("x", degrees=15, output_name="pelvis_x_pos15")
    test_pelvis("x", degrees=-15, output_name="pelvis_x_neg15")
    
    test_pelvis("y", degrees=15, output_name="pelvis_y_pos15")
    test_pelvis("y", degrees=-15, output_name="pelvis_y_neg15")
    
    test_pelvis("z", degrees=15, output_name="pelvis_z_pos15")
    test_pelvis("z", degrees=-15, output_name="pelvis_z_neg15")
    
    print("\n=== Done! Open meshes in Blender to see results ===")
    print("Looking for: which axis tilts left hip down vs right hip down")
