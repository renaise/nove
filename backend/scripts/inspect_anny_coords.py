import torch
import trimesh
import numpy as np
from anny import create_fullbody_model

def create_axis_marker(origin=[0,0,0], length=0.1):
    # X axis - Red
    x_axis = trimesh.creation.cylinder(radius=0.005, height=length, sections=8)
    x_axis.apply_transform(trimesh.transformations.rotation_matrix(np.pi/2, [0, 1, 0]))
    x_axis.apply_translation(np.array(origin) + np.array([length/2, 0, 0]))
    x_axis.visual.vertex_colors = [255, 0, 0, 255]

    # Y axis - Green
    y_axis = trimesh.creation.cylinder(radius=0.005, height=length, sections=8)
    y_axis.apply_transform(trimesh.transformations.rotation_matrix(np.pi/2, [1, 0, 0]))
    y_axis.apply_translation(np.array(origin) + np.array([0, length/2, 0]))
    y_axis.visual.vertex_colors = [0, 255, 0, 255]

    # Z axis - Blue
    z_axis = trimesh.creation.cylinder(radius=0.005, height=length, sections=8)
    z_axis.apply_translation(np.array(origin) + np.array([0, 0, length/2]))
    z_axis.visual.vertex_colors = [0, 0, 255, 255]

    return [x_axis, y_axis, z_axis]

def main():
    print("Loading ANNY model...")
    model = create_fullbody_model(
        rig="default",
        topology="default",
        remove_unattached_vertices=True,
        triangulate_faces=True,
    )
    
    # Generate rest pose
    output = model(
        pose_parameters=None,
        phenotype_kwargs={'height': torch.tensor([[0.5]]), 'gender': torch.tensor([[0.5]])},
        return_bone_ends=True
    )
    
    vertices = output["vertices"][0].detach().cpu().numpy()
    faces = model.get_triangular_faces().cpu().numpy()
    bone_heads = output["bone_heads"][0].detach().cpu().numpy()
    bone_labels = model.bone_labels
    
    mesh = trimesh.Trimesh(vertices=vertices, faces=faces)
    
    # Add axes at origin
    axes = create_axis_marker([0,0,0], length=0.5)
    
    # Add sphere at Pelvis (root)
    root_idx = bone_labels.index('root')
    pelvis_pos = bone_heads[root_idx]
    print(f"Pelvis position: {pelvis_pos}")
    
    pelvis_sphere = trimesh.creation.icosphere(radius=0.05)
    pelvis_sphere.apply_translation(pelvis_pos)
    pelvis_sphere.visual.vertex_colors = [255, 0, 255, 255] # Magenta
    
    # Combine
    scene = trimesh.util.concatenate([mesh] + axes + [pelvis_sphere])
    scene.export('debug_anny_coords.ply')
    print("Saved debug_anny_coords.ply")
    
    # Analyze bounds
    print(f"X range: {vertices[:,0].min():.3f} to {vertices[:,0].max():.3f}")
    print(f"Y range: {vertices[:,1].min():.3f} to {vertices[:,1].max():.3f}")
    print(f"Z range: {vertices[:,2].min():.3f} to {vertices[:,2].max():.3f}")
    
    if vertices[:,2].max() - vertices[:,2].min() > vertices[:,1].max() - vertices[:,1].min():
        print("Model appears to be Z-up (Height is Z)")
    else:
        print("Model appears to be Y-up (Height is Y)")

if __name__ == "__main__":
    main()
