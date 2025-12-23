#!/usr/bin/env python3
"""Generate reference pelvis mesh with no rotation."""

import numpy as np
import torch
import trimesh
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

# Identity pose (no rotations)
pose_params = torch.eye(4).unsqueeze(0).unsqueeze(0).repeat(1, num_bones, 1, 1)

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

mesh = trimesh.Trimesh(vertices=vertices, faces=faces, process=False)
mesh.export("/Users/jonathan/projects/wedding-app/backend/pelvis_0.ply")
print("Saved: pelvis_0.ply (reference - no rotation)")
