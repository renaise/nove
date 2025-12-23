#!/usr/bin/env python3
"""Test raising right arm as if holding something to face."""

import numpy as np
import torch
import trimesh
from scipy.spatial.transform import Rotation
from anny import create_fullbody_model

# Create model
model = create_fullbody_model(
    rig="default",
    topology="default",
    remove_unattached_vertices=True,
    triangulate_faces=True,
)
model = model.to(device="cpu", dtype=torch.float32)

num_bones = len(model.bone_labels)
bone_labels = model.bone_labels

print(f"Bones: {bone_labels}")

# Find bone indices
def get_bone_idx(name):
    return bone_labels.index(name)

output_dir = "/Users/jonathan/projects/wedding-app/backend"

phenotypes = {
    "gender": torch.tensor([[1.0]]),
    "age": torch.tensor([[0.5]]),
    "height": torch.tensor([[0.5]]),
    "weight": torch.tensor([[0.5]]),
    "muscle": torch.tensor([[0.5]]),
    "proportions": torch.tensor([[0.5]]),
}

def make_rotation_matrix(axis, angle_deg):
    """Create 4x4 rotation matrix around axis (x, y, or z)."""
    angle = np.radians(angle_deg)
    if axis == 'x':
        r = Rotation.from_rotvec([angle, 0, 0])
    elif axis == 'y':
        r = Rotation.from_rotvec([0, angle, 0])
    elif axis == 'z':
        r = Rotation.from_rotvec([0, 0, angle])
    else:
        raise ValueError(f"Unknown axis: {axis}")

    mat = np.eye(4)
    mat[:3, :3] = r.as_matrix()
    return mat

def generate_mesh(pose_dict, filename):
    """Generate mesh with given pose and save."""
    pose_params = torch.eye(4).unsqueeze(0).unsqueeze(0).repeat(1, num_bones, 1, 1)

    for bone_name, rotation_mat in pose_dict.items():
        idx = get_bone_idx(bone_name)
        pose_params[0, idx] = torch.from_numpy(rotation_mat).float()

    output = model(
        pose_parameters=pose_params,
        phenotype_kwargs=phenotypes,
        pose_parameterization="rest_relative",
    )

    vertices = output["vertices"][0].detach().cpu().numpy()
    faces = model.get_triangular_faces().cpu().numpy()

    mesh = trimesh.Trimesh(vertices=vertices, faces=faces, process=False)
    path = f"{output_dir}/{filename}"
    mesh.export(path)
    print(f"Saved: {path}")

# Reference: T-pose (no rotation)
generate_mesh({}, "arm_tpose.ply")

# Test 1: Right upper arm - rotate forward (X-axis)
# From T-pose, arm pointing sideways, rotate forward to point in front
print("\n=== Testing right arm forward (X-axis) ===")
generate_mesh({
    "upperarm01.R": make_rotation_matrix('x', -45),
}, "arm_right_x_neg45.ply")

generate_mesh({
    "upperarm01.R": make_rotation_matrix('x', -90),
}, "arm_right_x_neg90.ply")

generate_mesh({
    "upperarm01.R": make_rotation_matrix('x', 45),
}, "arm_right_x_pos45.ply")

# Test 2: Right upper arm - rotate inward (Z-axis) to bring toward body
print("\n=== Testing right arm inward (Z-axis) ===")
generate_mesh({
    "upperarm01.R": make_rotation_matrix('z', 45),
}, "arm_right_z_pos45.ply")

generate_mesh({
    "upperarm01.R": make_rotation_matrix('z', 90),
}, "arm_right_z_pos90.ply")

# Test 3: Combined - forward and inward (like reaching to face)
# Previous attempts went backward. Try positive X to go forward.
print("\n=== Testing combined rotations (reaching to face) ===")

# Try: Z+ brings arm in, X+ should bring arm forward
combined_1 = make_rotation_matrix('x', 60) @ make_rotation_matrix('z', 45)
generate_mesh({
    "upperarm01.R": combined_1,
}, "arm_right_reach_face_v1.ply")

# More forward, more inward
combined_2 = make_rotation_matrix('x', 90) @ make_rotation_matrix('z', 60)
generate_mesh({
    "upperarm01.R": combined_2,
}, "arm_right_reach_face_v2.ply")

# Test 4: Add elbow bend - forearm bends to bring hand toward face
# Z rotation is sensitive - too much pushes elbow into body
print("\n=== Testing with elbow bend ===")

# v1: Good pose, add Y twist to forearm to rotate palm toward face
generate_mesh({
    "upperarm01.R": make_rotation_matrix('x', 60) @ make_rotation_matrix('z', 25),
    "lowerarm01.R": make_rotation_matrix('x', 90) @ make_rotation_matrix('y', 45),  # Twist palm inward
}, "arm_right_reach_face_bent_v1.ply")

# v1b: Try opposite Y direction
generate_mesh({
    "upperarm01.R": make_rotation_matrix('x', 60) @ make_rotation_matrix('z', 25),
    "lowerarm01.R": make_rotation_matrix('x', 90) @ make_rotation_matrix('y', -45),  # Twist palm other way
}, "arm_right_reach_face_bent_v1b.ply")

# v2: Hand to neck pose (keeping as reference)
generate_mesh({
    "upperarm01.R": make_rotation_matrix('x', 75) @ make_rotation_matrix('z', 30),
    "lowerarm01.R": make_rotation_matrix('x', 110),
}, "arm_right_reach_face_bent_v2.ply")

# Test 5: LEFT arm holding to face (mirrored from right)
# Z inward: opposite sign (right=+Z, left=-Z)
# X forward: same sign (+X for both)
# Y palm twist: opposite sign (right=+Y inward, left=-Y inward)
print("\n=== Testing LEFT arm holding to face ===")
generate_mesh({
    "upperarm01.L": make_rotation_matrix('x', 60) @ make_rotation_matrix('z', -25),
    "lowerarm01.L": make_rotation_matrix('x', 90) @ make_rotation_matrix('y', -45),
}, "arm_left_reach_face_bent_v1.ply")

# Test 6: Y-axis rotation (twist)
print("\n=== Testing Y-axis (twist) ===")
generate_mesh({
    "upperarm01.R": make_rotation_matrix('y', 45),
}, "arm_right_y_pos45.ply")

generate_mesh({
    "upperarm01.R": make_rotation_matrix('y', -45),
}, "arm_right_y_neg45.ply")

print("\n=== Done! ===")
print("Check the .ply files in Blender to see which rotation achieves the desired pose.")
