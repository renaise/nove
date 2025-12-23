#!/usr/bin/env python3
"""Test Dancer's Pose (Natarajasana) - 10 targeted attempts based on learnings."""

import numpy as np
import torch
import trimesh
from scipy.spatial.transform import Rotation
from anny import create_fullbody_model

model = create_fullbody_model(
    rig="default",
    topology="default",
    remove_unattached_vertices=True,
    triangulate_faces=True,
)
model = model.to(device="cpu", dtype=torch.float32)

num_bones = len(model.bone_labels)
bone_labels = model.bone_labels

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

print("=== Dancer's Pose - 10 Attempts ===\n")

# Dancer's Pose breakdown:
# - Standing on LEFT leg
# - RIGHT leg: bent backward, foot reaching up toward head
# - RIGHT arm: reaching back to grab the foot
# - LEFT arm: extended forward for balance
#
# Based on learnings:
# - Legs: -X = forward, so +X = backward
# - Arms: +X = forward, so -X = backward
# - pelvis.R: controls leg direction (use for backward extension)
# - For backward leg: pelvis Y might be minimal (not twisting inward like tree pose)

# Attempt 1: Basic backward leg extension
print("v01: Basic backward extension")
generate_mesh({
    # Right leg backward
    "pelvis.R": make_rotation_matrix('x', 20),  # Tilt pelvis to extend leg back
    "upperleg01.R": make_rotation_matrix('x', 30),  # Extend thigh backward
    "lowerleg01.R": make_rotation_matrix('x', 90),  # Bend knee
    # Right arm reaching back
    "upperarm01.R": make_rotation_matrix('x', -60) @ make_rotation_matrix('z', 30),
    "lowerarm01.R": make_rotation_matrix('x', 45),
    # Left arm forward
    "upperarm01.L": make_rotation_matrix('x', 60) @ make_rotation_matrix('z', -20),
}, "dancer_pose_v01.ply")

# Attempt 2: More pelvis involvement
print("v02: More pelvis rotation")
generate_mesh({
    "pelvis.R": make_rotation_matrix('x', 30) @ make_rotation_matrix('z', -10),
    "upperleg01.R": make_rotation_matrix('x', 40),
    "lowerleg01.R": make_rotation_matrix('x', 100),
    "upperarm01.R": make_rotation_matrix('x', -70) @ make_rotation_matrix('z', 40),
    "lowerarm01.R": make_rotation_matrix('x', 60),
    "upperarm01.L": make_rotation_matrix('x', 70) @ make_rotation_matrix('z', -25),
}, "dancer_pose_v02.ply")

# Attempt 3: Higher leg lift
print("v03: Higher leg lift")
generate_mesh({
    "pelvis.R": make_rotation_matrix('x', 40) @ make_rotation_matrix('z', -15),
    "upperleg01.R": make_rotation_matrix('x', 50),
    "lowerleg01.R": make_rotation_matrix('x', 110),
    "foot.R": make_rotation_matrix('x', -30),  # Point toes
    "upperarm01.R": make_rotation_matrix('x', -80) @ make_rotation_matrix('z', 45),
    "lowerarm01.R": make_rotation_matrix('x', 70),
    "upperarm01.L": make_rotation_matrix('x', 80) @ make_rotation_matrix('z', -20),
}, "dancer_pose_v03.ply")

# Attempt 4: Try pelvis Y rotation for leg direction
print("v04: Add pelvis Y rotation")
generate_mesh({
    "pelvis.R": make_rotation_matrix('x', 35) @ make_rotation_matrix('y', -20) @ make_rotation_matrix('z', -10),
    "upperleg01.R": make_rotation_matrix('x', 45),
    "lowerleg01.R": make_rotation_matrix('x', 105),
    "foot.R": make_rotation_matrix('x', -25),
    "upperarm01.R": make_rotation_matrix('x', -75) @ make_rotation_matrix('z', 35),
    "lowerarm01.R": make_rotation_matrix('x', 65),
    "upperarm01.L": make_rotation_matrix('x', 75) @ make_rotation_matrix('z', -25),
}, "dancer_pose_v04.ply")

# Attempt 5: More extreme leg extension
print("v05: Extreme leg extension")
generate_mesh({
    "pelvis.R": make_rotation_matrix('x', 50) @ make_rotation_matrix('z', -20),
    "upperleg01.R": make_rotation_matrix('x', 60),
    "lowerleg01.R": make_rotation_matrix('x', 120),
    "foot.R": make_rotation_matrix('x', -40),
    "upperarm01.R": make_rotation_matrix('x', -90) @ make_rotation_matrix('z', 50),
    "lowerarm01.R": make_rotation_matrix('x', 80),
    "upperarm01.L": make_rotation_matrix('x', 90) @ make_rotation_matrix('z', -20),
}, "dancer_pose_v05.ply")

# Attempt 6: Focus on arm reaching back properly
print("v06: Better arm reach")
generate_mesh({
    "pelvis.R": make_rotation_matrix('x', 35) @ make_rotation_matrix('z', -15),
    "upperleg01.R": make_rotation_matrix('x', 45),
    "lowerleg01.R": make_rotation_matrix('x', 100),
    # Arm reaching back and down
    "upperarm01.R": make_rotation_matrix('x', -60) @ make_rotation_matrix('z', 60) @ make_rotation_matrix('y', -20),
    "lowerarm01.R": make_rotation_matrix('x', 90),
    "upperarm01.L": make_rotation_matrix('x', 70) @ make_rotation_matrix('z', -30),
}, "dancer_pose_v06.ply")

# Attempt 7: Try different approach - less pelvis, more upperleg
print("v07: More upperleg, less pelvis")
generate_mesh({
    "pelvis.R": make_rotation_matrix('x', 20),
    "upperleg01.R": make_rotation_matrix('x', 60) @ make_rotation_matrix('z', -10),
    "lowerleg01.R": make_rotation_matrix('x', 115),
    "foot.R": make_rotation_matrix('x', -30),
    "upperarm01.R": make_rotation_matrix('x', -70) @ make_rotation_matrix('z', 50),
    "lowerarm01.R": make_rotation_matrix('x', 75),
    "upperarm01.L": make_rotation_matrix('x', 80) @ make_rotation_matrix('z', -25),
}, "dancer_pose_v07.ply")

# Attempt 8: Add body forward lean (spine)
print("v08: Add spine forward lean")
generate_mesh({
    "spine01": make_rotation_matrix('x', 15),  # Lean torso forward
    "pelvis.R": make_rotation_matrix('x', 40) @ make_rotation_matrix('z', -15),
    "upperleg01.R": make_rotation_matrix('x', 50),
    "lowerleg01.R": make_rotation_matrix('x', 110),
    "foot.R": make_rotation_matrix('x', -30),
    "upperarm01.R": make_rotation_matrix('x', -80) @ make_rotation_matrix('z', 45),
    "lowerarm01.R": make_rotation_matrix('x', 70),
    "upperarm01.L": make_rotation_matrix('x', 85) @ make_rotation_matrix('z', -20),
}, "dancer_pose_v08.ply")

# Attempt 9: Moderate balanced pose
print("v09: Balanced moderate pose")
generate_mesh({
    "spine01": make_rotation_matrix('x', 10),
    "pelvis.R": make_rotation_matrix('x', 30) @ make_rotation_matrix('z', -10),
    "upperleg01.R": make_rotation_matrix('x', 40),
    "lowerleg01.R": make_rotation_matrix('x', 95),
    "foot.R": make_rotation_matrix('x', -20),
    "upperarm01.R": make_rotation_matrix('x', -65) @ make_rotation_matrix('z', 40),
    "lowerarm01.R": make_rotation_matrix('x', 60),
    "upperarm01.L": make_rotation_matrix('x', 70) @ make_rotation_matrix('z', -25),
}, "dancer_pose_v09.ply")

# Attempt 10: Graceful variation with neck
print("v10: Graceful with head position")
generate_mesh({
    "spine01": make_rotation_matrix('x', 12),
    "neck01": make_rotation_matrix('x', -10),  # Head up slightly
    "pelvis.R": make_rotation_matrix('x', 35) @ make_rotation_matrix('z', -12),
    "upperleg01.R": make_rotation_matrix('x', 45),
    "lowerleg01.R": make_rotation_matrix('x', 105),
    "foot.R": make_rotation_matrix('x', -25),
    "upperarm01.R": make_rotation_matrix('x', -75) @ make_rotation_matrix('z', 45),
    "lowerarm01.R": make_rotation_matrix('x', 70),
    "wrist.R": make_rotation_matrix('x', 20),  # Wrist to grab foot
    "upperarm01.L": make_rotation_matrix('x', 80) @ make_rotation_matrix('z', -22),
}, "dancer_pose_v10.ply")

print("\n=== Done! Check dancer_pose_v*.ply files ===")
