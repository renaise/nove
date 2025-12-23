#!/usr/bin/env python3
"""Test Tree Pose (Vrksasana) - standing on left leg, right leg bent to side."""

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

# Tree Pose breakdown:
# - Left leg: standing straight (no rotation needed)
# - Right leg: lifted, externally rotated, knee bent, knee pointing right
#
# Right leg rotations needed:
# - Y rotation: external rotation (twist leg outward) - based on docs: -Y = outward for right leg
# - Z rotation: abduct (move leg away from body to side) - +Z = outward for right leg?
#   Wait, docs say -Z brings legs together for right leg, so +Z should abduct
#   But docs also say legs are opposite to arms... let me check
#   Actually: "Right leg: -Z rotation" to bring TOGETHER, so +Z = apart/abduct
# - X rotation: slight forward lift
# - Lower leg X: bend knee

print("=== Tree Pose Combined (v019 knee + v952 foot height + foot Z) ===\n")

# v019: px=-15, py=45, pz=25, uz=30, lx=110 - good knee position
# v952: px=-5, py=60, pz=35, uz=20, lx=130 - foot behind other leg
# v924: knee too inward
# Need: connect foot to standing leg - try foot Z rotation

import os
os.makedirs(f"{output_dir}/tree_pose_combined", exist_ok=True)

count = 0

# Combine best attributes
pelvis_x_vals = [-15, -10]              # v019 had -15
pelvis_y_vals = [45, 50, 55]            # v019 had 45
pelvis_z_vals = [20, 25, 30]            # v019 had 25, reduce to bring foot closer

upper_z_vals = [25, 30, 35]             # v019 had 30, try more for knee out

lower_x_vals = [115, 120, 125, 130]     # Between v019's 110 and v952's 130

# Foot rotations to connect to standing leg
foot_z_vals = [-30, -15, 0, 15, 30]     # Swing foot inward/outward

for pelvis_x in pelvis_x_vals:
    for pelvis_y in pelvis_y_vals:
        for pelvis_z in pelvis_z_vals:
            for upper_z in upper_z_vals:
                for lower_x in lower_x_vals:
                    for foot_z in foot_z_vals:
                        count += 1

                        filename = f"tree_pose_combined/v{count:03d}_px{pelvis_x}_py{pelvis_y}_pz{pelvis_z}_uz{upper_z}_lx{lower_x}_fz{foot_z}.ply"

                        pose = {
                            "pelvis.R": (
                                make_rotation_matrix('x', pelvis_x) @
                                make_rotation_matrix('y', pelvis_y) @
                                make_rotation_matrix('z', pelvis_z)
                            ),
                            "upperleg01.R": (
                                make_rotation_matrix('z', upper_z) @
                                make_rotation_matrix('x', -10)
                            ),
                            "lowerleg01.R": make_rotation_matrix('x', lower_x),
                        }
                        if foot_z != 0:
                            pose["foot.R"] = make_rotation_matrix('z', foot_z)

                        generate_mesh(pose, filename)

print(f"\n=== Generated {count} variations in tree_pose_combined/ ===")
print("Filename format: v##_uy{Y}_uz{Z}_ux{X}_lx{knee}_lz{swing}.ply")
print("  uy = upper leg Y (external rotation)")
print("  uz = upper leg Z (abduction)")
print("  ux = upper leg X (forward)")
print("  lx = lower leg X (knee bend)")
print("  lz = lower leg Z (swing)")

# Skip old attempts
import sys
sys.exit(0)

# Attempt 2: More external rotation, less abduction
print("Attempt 2: More external rotation")
generate_mesh({
    "upperleg01.R": (
        make_rotation_matrix('y', -45) @  # More external rotation
        make_rotation_matrix('z', 10) @   # Less abduction
        make_rotation_matrix('x', -5)     # Minimal forward
    ),
    "lowerleg01.R": make_rotation_matrix('x', 100),  # More bent knee
}, "tree_pose_v2.ply")

# Attempt 3: Focus on getting knee to point right
# Maybe we need more Z (abduction) and less Y
print("Attempt 3: More abduction focus")
generate_mesh({
    "upperleg01.R": (
        make_rotation_matrix('z', 20) @   # Abduct first
        make_rotation_matrix('y', -25) @  # Then external rotation
        make_rotation_matrix('x', -15)    # Some forward lift
    ),
    "lowerleg01.R": make_rotation_matrix('x', 110),
}, "tree_pose_v3.ply")

# Attempt 4: Add arms overhead (classic tree pose)
print("Attempt 4: Full tree pose with arms")
generate_mesh({
    # Right leg (same as v2)
    "upperleg01.R": (
        make_rotation_matrix('y', -45) @
        make_rotation_matrix('z', 10) @
        make_rotation_matrix('x', -5)
    ),
    "lowerleg01.R": make_rotation_matrix('x', 100),
    # Arms raised overhead
    # From T-pose, need to rotate arms UP (toward head)
    # For right arm: +Z brings inward, so more +Z to bring up toward center
    # Also need X rotation to bring forward/up
    "upperarm01.R": (
        make_rotation_matrix('z', 150) @  # Bring arm up and over head
        make_rotation_matrix('x', 20)     # Slight forward
    ),
    "upperarm01.L": (
        make_rotation_matrix('z', -150) @ # Mirror for left arm
        make_rotation_matrix('x', 20)
    ),
}, "tree_pose_v4_full.ply")

print("\n=== Done! ===")
print("Check the tree_pose_*.ply files in Blender")
