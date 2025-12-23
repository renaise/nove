#!/usr/bin/env python3
"""
Calculate the angular offset of a body mesh relative to the vertical axis.

This script determines how much a mesh is tilted/rotated from a perfectly
upright position by analyzing the spine axis (pelvis-to-head direction).

Methods used:
1. PCA on torso vertices - finds the principal axis of the body
2. Pelvis-to-head vector - uses keypoints if available
3. Hip-to-shoulder vector - fallback using mesh slices

Usage:
    python scripts/calculate_mesh_angle.py <mesh.ply> [keypoints.json]
"""

import sys
from pathlib import Path
import numpy as np
import trimesh
from scipy.spatial.transform import Rotation


def calculate_spine_axis_pca(mesh: trimesh.Trimesh) -> np.ndarray:
    """
    Calculate the spine axis using PCA on the central torso vertices.

    Returns:
        Unit vector pointing from pelvis toward head (approximately +Z in ANNY space)
    """
    verts = mesh.vertices
    min_z = verts[:, 2].min()
    max_z = verts[:, 2].max()
    height = max_z - min_z

    # Select torso region (40% to 75% of height) and central X region
    torso_mask = (verts[:, 2] > min_z + height * 0.40) & (verts[:, 2] < min_z + height * 0.75)
    # Central X: within 15% of center
    x_center = verts[:, 0].mean()
    central_mask = np.abs(verts[:, 0] - x_center) < 0.15

    combined_mask = torso_mask & central_mask
    if combined_mask.sum() < 50:
        # Fallback: just use torso mask
        combined_mask = torso_mask

    torso_verts = verts[combined_mask]

    # PCA to find principal axis
    centered = torso_verts - torso_verts.mean(axis=0)
    cov = np.cov(centered.T)
    eigenvalues, eigenvectors = np.linalg.eigh(cov)

    # Largest eigenvalue corresponds to longest axis (spine direction)
    spine_axis = eigenvectors[:, np.argmax(eigenvalues)]

    # Ensure it points upward (+Z)
    if spine_axis[2] < 0:
        spine_axis = -spine_axis

    return spine_axis / np.linalg.norm(spine_axis)


def calculate_spine_axis_slices(mesh: trimesh.Trimesh) -> np.ndarray:
    """
    Calculate spine axis by finding centroids at pelvis and shoulder levels.

    Returns:
        Unit vector pointing from pelvis toward shoulders
    """
    verts = mesh.vertices
    min_z = verts[:, 2].min()
    max_z = verts[:, 2].max()
    height = max_z - min_z

    # Get centroid at pelvis level (50%)
    pelvis_z = min_z + height * 0.50
    pelvis_path = mesh.section(plane_normal=[0, 0, 1], plane_origin=[0, 0, pelvis_z])
    if pelvis_path and pelvis_path.discrete:
        # Find largest loop (torso, not legs)
        largest = max(pelvis_path.discrete, key=lambda l: len(l))
        pelvis_center = np.array([largest[:, 0].mean(), largest[:, 1].mean(), pelvis_z])
    else:
        pelvis_center = np.array([0, 0, pelvis_z])

    # Get centroid at shoulder level (75%)
    shoulder_z = min_z + height * 0.75
    shoulder_path = mesh.section(plane_normal=[0, 0, 1], plane_origin=[0, 0, shoulder_z])
    if shoulder_path and shoulder_path.discrete:
        # Find torso loop (most central)
        loops = list(shoulder_path.discrete)
        centers = [np.array([l[:, 0].mean(), l[:, 1].mean(), shoulder_z]) for l in loops]
        # Pick the one closest to pelvis X/Y
        torso_center = min(centers, key=lambda c: np.abs(c[0] - pelvis_center[0]) + np.abs(c[1] - pelvis_center[1]))
    else:
        torso_center = np.array([0, 0, shoulder_z])

    spine_axis = torso_center - pelvis_center
    return spine_axis / np.linalg.norm(spine_axis)


def calculate_spine_axis_keypoints(keypoints_3d: np.ndarray) -> np.ndarray:
    """
    Calculate spine axis from SAM-3D keypoints (pelvis to head/neck).

    Args:
        keypoints_3d: Transformed keypoints in ANNY space (Z-up, pelvis-centered)

    Returns:
        Unit vector pointing from pelvis toward head
    """
    # Use neck (index 69) or head (index 0) and pelvis (midpoint of 9, 10)
    pelvis = (keypoints_3d[9] + keypoints_3d[10]) / 2
    neck = keypoints_3d[69] if len(keypoints_3d) > 69 else keypoints_3d[0]

    spine_axis = neck - pelvis
    return spine_axis / np.linalg.norm(spine_axis)


def axis_to_angles(axis: np.ndarray) -> dict:
    """
    Calculate the tilt angles of an axis relative to vertical (Z-up).

    Returns:
        Dictionary with:
        - total_tilt: Total angle from vertical (degrees)
        - x_tilt: Forward/backward tilt (rotation around X axis, degrees)
        - y_tilt: Side-to-side tilt (rotation around Y axis, degrees)
    """
    # Vertical reference
    vertical = np.array([0, 0, 1])

    # Total tilt from vertical
    total_tilt = np.arccos(np.clip(np.dot(axis, vertical), -1, 1))

    # Project axis onto XZ plane (forward/back tilt)
    axis_xz = np.array([axis[0], 0, axis[2]])
    axis_xz_norm = np.linalg.norm(axis_xz)
    if axis_xz_norm > 1e-6:
        axis_xz /= axis_xz_norm
        # Angle in XZ plane - positive = tilted forward (toward +Y)
        # Actually for body tilt: X tilt is when head moves in X direction
        x_tilt = np.arctan2(axis[0], axis[2])  # Tilt in X direction
    else:
        x_tilt = 0

    # Project axis onto YZ plane (side tilt)
    axis_yz = np.array([0, axis[1], axis[2]])
    axis_yz_norm = np.linalg.norm(axis_yz)
    if axis_yz_norm > 1e-6:
        axis_yz /= axis_yz_norm
        # Angle in YZ plane - positive = tilted sideways (toward +Y)
        y_tilt = np.arctan2(axis[1], axis[2])
    else:
        y_tilt = 0

    return {
        'total_tilt_deg': np.degrees(total_tilt),
        'x_tilt_deg': np.degrees(x_tilt),  # Tilt in X direction (left/right lean)
        'y_tilt_deg': np.degrees(y_tilt),  # Tilt in Y direction (forward/back lean)
        'axis': axis,
    }


def calculate_rotation_to_vertical(axis: np.ndarray) -> np.ndarray:
    """
    Calculate the rotation matrix needed to align the axis with vertical (+Z).

    Returns:
        3x3 rotation matrix that, when applied to the mesh, would make it upright
    """
    vertical = np.array([0, 0, 1])

    # Rotation axis is perpendicular to both
    rot_axis = np.cross(axis, vertical)
    rot_axis_norm = np.linalg.norm(rot_axis)

    if rot_axis_norm < 1e-6:
        # Already aligned (or exactly opposite)
        if np.dot(axis, vertical) > 0:
            return np.eye(3)
        else:
            # 180 degree rotation around X
            return np.array([[1, 0, 0], [0, -1, 0], [0, 0, -1]])

    rot_axis /= rot_axis_norm
    angle = np.arccos(np.clip(np.dot(axis, vertical), -1, 1))

    # Rodrigues rotation
    R = Rotation.from_rotvec(rot_axis * angle).as_matrix()
    return R


def analyze_mesh(mesh_path: str, keypoints_path: str = None) -> dict:
    """
    Analyze a mesh and calculate its angular offset from vertical.

    Args:
        mesh_path: Path to PLY file
        keypoints_path: Optional path to keypoints JSON

    Returns:
        Dictionary with analysis results
    """
    mesh = trimesh.load(mesh_path)
    verts = np.array(mesh.vertices)

    print(f"\n{'='*60}")
    print(f"Analyzing: {Path(mesh_path).name}")
    print(f"{'='*60}")

    # Basic mesh info
    print(f"\nMesh bounds:")
    print(f"  X: [{verts[:,0].min():.4f}, {verts[:,0].max():.4f}]")
    print(f"  Y: [{verts[:,1].min():.4f}, {verts[:,1].max():.4f}]")
    print(f"  Z: [{verts[:,2].min():.4f}, {verts[:,2].max():.4f}]")

    height = verts[:, 2].max() - verts[:, 2].min()
    print(f"  Height: {height:.4f}")

    results = {
        'mesh_path': mesh_path,
        'height': height,
        'methods': {}
    }

    # Method 1: PCA on torso
    print(f"\n--- Method 1: PCA on torso vertices ---")
    try:
        axis_pca = calculate_spine_axis_pca(mesh)
        angles_pca = axis_to_angles(axis_pca)
        results['methods']['pca'] = angles_pca
        print(f"  Spine axis: [{axis_pca[0]:+.4f}, {axis_pca[1]:+.4f}, {axis_pca[2]:+.4f}]")
        print(f"  Total tilt from vertical: {angles_pca['total_tilt_deg']:.2f}°")
        print(f"  X-tilt (left/right lean): {angles_pca['x_tilt_deg']:+.2f}°")
        print(f"  Y-tilt (forward/back):    {angles_pca['y_tilt_deg']:+.2f}°")
    except Exception as e:
        print(f"  Error: {e}")

    # Method 2: Slice centroids
    print(f"\n--- Method 2: Pelvis-to-shoulder centroids ---")
    try:
        axis_slices = calculate_spine_axis_slices(mesh)
        angles_slices = axis_to_angles(axis_slices)
        results['methods']['slices'] = angles_slices
        print(f"  Spine axis: [{axis_slices[0]:+.4f}, {axis_slices[1]:+.4f}, {axis_slices[2]:+.4f}]")
        print(f"  Total tilt from vertical: {angles_slices['total_tilt_deg']:.2f}°")
        print(f"  X-tilt (left/right lean): {angles_slices['x_tilt_deg']:+.2f}°")
        print(f"  Y-tilt (forward/back):    {angles_slices['y_tilt_deg']:+.2f}°")
    except Exception as e:
        print(f"  Error: {e}")

    # Method 3: Keypoints (if available)
    if keypoints_path:
        print(f"\n--- Method 3: SAM-3D keypoints ---")
        try:
            import json
            with open(keypoints_path) as f:
                data = json.load(f)
            if 'metadata' in data and 'people' in data['metadata']:
                kp = np.array(data['metadata']['people'][0]['keypoints_3d'])
            else:
                kp = np.array(data['keypoints_3d'])

            # Transform to ANNY space (same as anny_integration.py)
            kp_ply = kp.copy()
            kp_ply[:, 1] *= -1  # Flip Y
            kp_transformed = kp_ply[:, [0, 2, 1]]  # X, Z, Y -> X, Y, Z

            axis_kp = calculate_spine_axis_keypoints(kp_transformed)
            angles_kp = axis_to_angles(axis_kp)
            results['methods']['keypoints'] = angles_kp
            print(f"  Spine axis: [{axis_kp[0]:+.4f}, {axis_kp[1]:+.4f}, {axis_kp[2]:+.4f}]")
            print(f"  Total tilt from vertical: {angles_kp['total_tilt_deg']:.2f}°")
            print(f"  X-tilt (left/right lean): {angles_kp['x_tilt_deg']:+.2f}°")
            print(f"  Y-tilt (forward/back):    {angles_kp['y_tilt_deg']:+.2f}°")
        except Exception as e:
            print(f"  Error: {e}")

    # Calculate correction rotation
    print(f"\n--- Correction rotation needed ---")
    # Use PCA result as primary
    if 'pca' in results['methods']:
        axis = results['methods']['pca']['axis']
        R = calculate_rotation_to_vertical(axis)
        euler = Rotation.from_matrix(R).as_euler('xyz', degrees=True)
        results['correction_rotation'] = R
        results['correction_euler_xyz'] = euler
        print(f"  Rotation to make vertical (Euler XYZ): [{euler[0]:+.2f}°, {euler[1]:+.2f}°, {euler[2]:+.2f}°]")

    return results


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/calculate_mesh_angle.py <mesh.ply> [keypoints.json]")
        sys.exit(1)

    mesh_path = sys.argv[1]
    keypoints_path = sys.argv[2] if len(sys.argv) > 2 else None

    if not Path(mesh_path).exists():
        print(f"Error: Mesh file not found: {mesh_path}")
        sys.exit(1)

    results = analyze_mesh(mesh_path, keypoints_path)

    # If there's a debug_anny_rest.ply in the same directory, analyze it too
    mesh_dir = Path(mesh_path).parent
    anny_rest_path = mesh_dir / "debug_anny_rest.ply"
    if anny_rest_path.exists():
        print("\n\n")
        anny_results = analyze_mesh(str(anny_rest_path))

        # Compare
        print(f"\n{'='*60}")
        print("COMPARISON: SAM-3D vs ANNY Rest")
        print(f"{'='*60}")

        if 'pca' in results['methods'] and 'pca' in anny_results['methods']:
            sam3d_tilt = results['methods']['pca']['total_tilt_deg']
            anny_tilt = anny_results['methods']['pca']['total_tilt_deg']
            print(f"  SAM-3D total tilt: {sam3d_tilt:.2f}°")
            print(f"  ANNY total tilt:   {anny_tilt:.2f}°")
            print(f"  Difference:        {sam3d_tilt - anny_tilt:+.2f}°")

            sam3d_x = results['methods']['pca']['x_tilt_deg']
            sam3d_y = results['methods']['pca']['y_tilt_deg']
            anny_x = anny_results['methods']['pca']['x_tilt_deg']
            anny_y = anny_results['methods']['pca']['y_tilt_deg']
            print(f"\n  X-tilt difference: {sam3d_x - anny_x:+.2f}°")
            print(f"  Y-tilt difference: {sam3d_y - anny_y:+.2f}°")


if __name__ == "__main__":
    main()
