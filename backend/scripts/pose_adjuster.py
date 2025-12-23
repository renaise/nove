#!/usr/bin/env python3
"""
Interactive Pose Adjuster Tool

Visualizes a mesh with joint positions and allows interactive adjustment.
Reports adjustments in ANNY coordinate space.

Usage:
    python pose_adjuster.py <mesh.ply> [--bone BONE_NAME]

Controls:
    - Mouse drag: Rotate view
    - Scroll: Zoom
    - Arrow keys: Adjust selected bone rotation
    - Q/W: Switch between X/Y/Z axis
    - +/-: Increase/decrease rotation step
    - P: Print current pose parameters
    - R: Reset to base pose
    - S: Save current mesh
"""

import argparse
import numpy as np
import torch
import trimesh
from scipy.spatial.transform import Rotation
from anny import create_fullbody_model

try:
    import open3d as o3d
    HAS_OPEN3D = True
except ImportError:
    HAS_OPEN3D = False

try:
    import pyvista as pv
    HAS_PYVISTA = True
except ImportError:
    HAS_PYVISTA = False


class PoseAdjuster:
    def __init__(self):
        print("Loading ANNY model...")
        self.model = create_fullbody_model(
            rig="default",
            topology="default",
            remove_unattached_vertices=True,
            triangulate_faces=True,
        )
        self.model = self.model.to(device="cpu", dtype=torch.float32)

        self.num_bones = len(self.model.bone_labels)
        self.bone_labels = self.model.bone_labels

        self.phenotypes = {
            "gender": torch.tensor([[1.0]]),
            "age": torch.tensor([[0.5]]),
            "height": torch.tensor([[0.5]]),
            "weight": torch.tensor([[0.5]]),
            "muscle": torch.tensor([[0.5]]),
            "proportions": torch.tensor([[0.5]]),
        }

        # Current pose state: {bone_name: {'x': deg, 'y': deg, 'z': deg}}
        self.pose_state = {}

        # Key bones for dancer pose
        self.key_bones = [
            "pelvis.R", "upperleg01.R", "lowerleg01.R", "foot.R",
            "pelvis.L", "upperleg01.L", "lowerleg01.L", "foot.L",
            "upperarm01.R", "lowerarm01.R", "wrist.R",
            "upperarm01.L", "lowerarm01.L", "wrist.L",
            "spine01", "spine02", "spine03",
            "neck01", "head",
            "root"
        ]

    def get_bone_idx(self, name):
        return self.bone_labels.index(name)

    def make_rotation_matrix(self, x_deg=0, y_deg=0, z_deg=0):
        """Create 4x4 rotation matrix from Euler angles."""
        r = Rotation.from_euler('xyz', [x_deg, y_deg, z_deg], degrees=True)
        mat = np.eye(4)
        mat[:3, :3] = r.as_matrix()
        return mat

    def generate_mesh_and_joints(self):
        """Generate mesh with current pose and return vertices, faces, and joint positions."""
        pose_params = torch.eye(4).unsqueeze(0).unsqueeze(0).repeat(1, self.num_bones, 1, 1)

        for bone_name, rotations in self.pose_state.items():
            if bone_name in self.bone_labels:
                idx = self.get_bone_idx(bone_name)
                mat = self.make_rotation_matrix(
                    rotations.get('x', 0),
                    rotations.get('y', 0),
                    rotations.get('z', 0)
                )
                pose_params[0, idx] = torch.from_numpy(mat).float()

        output = self.model(
            pose_parameters=pose_params,
            phenotype_kwargs=self.phenotypes,
            pose_parameterization="rest_relative",
            return_bone_ends=True,
        )

        vertices = output["vertices"][0].detach().cpu().numpy()
        faces = self.model.get_triangular_faces().cpu().numpy()
        bone_heads = output["bone_heads"][0].detach().cpu().numpy()
        bone_tails = output["bone_tails"][0].detach().cpu().numpy()

        return vertices, faces, bone_heads, bone_tails

    def print_joint_positions(self, bone_heads, bone_tails):
        """Print positions of key joints."""
        print("\n=== Joint Positions (ANNY coordinates) ===")
        print(f"{'Bone':<20} {'Head X':>8} {'Head Y':>8} {'Head Z':>8} | {'Tail X':>8} {'Tail Y':>8} {'Tail Z':>8}")
        print("-" * 90)

        for bone_name in self.key_bones:
            if bone_name in self.bone_labels:
                idx = self.get_bone_idx(bone_name)
                head = bone_heads[idx]
                tail = bone_tails[idx]
                print(f"{bone_name:<20} {head[0]:>8.3f} {head[1]:>8.3f} {head[2]:>8.3f} | {tail[0]:>8.3f} {tail[1]:>8.3f} {tail[2]:>8.3f}")

    def print_pose_state(self):
        """Print current pose parameters."""
        print("\n=== Current Pose Parameters ===")
        print("pose = {")
        for bone_name, rotations in sorted(self.pose_state.items()):
            x, y, z = rotations.get('x', 0), rotations.get('y', 0), rotations.get('z', 0)
            if x != 0 or y != 0 or z != 0:
                parts = []
                if x != 0:
                    parts.append(f"rotation_x({x})")
                if y != 0:
                    parts.append(f"rotation_y({y})")
                if z != 0:
                    parts.append(f"rotation_z({z})")
                print(f'    "{bone_name}": {" @ ".join(parts)},')
        print("}")

    def set_bone_rotation(self, bone_name, axis, value):
        """Set rotation for a specific bone and axis."""
        if bone_name not in self.pose_state:
            self.pose_state[bone_name] = {'x': 0, 'y': 0, 'z': 0}
        self.pose_state[bone_name][axis] = value

    def adjust_bone_rotation(self, bone_name, axis, delta):
        """Adjust rotation for a specific bone and axis by delta degrees."""
        if bone_name not in self.pose_state:
            self.pose_state[bone_name] = {'x': 0, 'y': 0, 'z': 0}
        self.pose_state[bone_name][axis] += delta
        return self.pose_state[bone_name][axis]

    def run_interactive_cli(self):
        """Run interactive CLI for adjusting pose."""
        print("\n=== Interactive Pose Adjuster ===")
        print("Commands:")
        print("  set <bone> <axis> <value>  - Set rotation (e.g., 'set pelvis.R x 30')")
        print("  adj <bone> <axis> <delta>  - Adjust rotation (e.g., 'adj pelvis.R x 5')")
        print("  show                       - Show current pose and joint positions")
        print("  save <filename>            - Save current mesh")
        print("  bones                      - List available bones")
        print("  reset                      - Reset all rotations")
        print("  quit                       - Exit")
        print()

        while True:
            try:
                cmd = input("pose> ").strip()
            except EOFError:
                break

            if not cmd:
                continue

            parts = cmd.split()
            action = parts[0].lower()  # Only lowercase the action, not bone names

            if action == 'quit' or action == 'q':
                break

            elif action == 'bones':
                print("\nKey bones:")
                for bone in self.key_bones:
                    print(f"  {bone}")
                print(f"\nAll bones ({len(self.bone_labels)}):")
                for i, bone in enumerate(self.bone_labels):
                    print(f"  {i:3d}: {bone}")

            elif action == 'reset':
                self.pose_state = {}
                print("Pose reset to T-pose")

            elif action == 'show':
                vertices, faces, bone_heads, bone_tails = self.generate_mesh_and_joints()
                self.print_pose_state()
                self.print_joint_positions(bone_heads, bone_tails)

            elif action == 'save' and len(parts) >= 2:
                filename = parts[1]
                if not filename.endswith('.ply'):
                    filename += '.ply'
                vertices, faces, _, _ = self.generate_mesh_and_joints()
                mesh = trimesh.Trimesh(vertices=vertices, faces=faces, process=False)
                mesh.export(filename)
                print(f"Saved: {filename}")

            elif action == 'set' and len(parts) >= 4:
                bone_name = parts[1]
                axis = parts[2].lower()
                try:
                    value = float(parts[3])
                    if bone_name in self.bone_labels and axis in ['x', 'y', 'z']:
                        self.set_bone_rotation(bone_name, axis, value)
                        print(f"Set {bone_name} {axis} = {value}°")
                        # Auto-save
                        vertices, faces, _, _ = self.generate_mesh_and_joints()
                        mesh = trimesh.Trimesh(vertices=vertices, faces=faces, process=False)
                        mesh.export("dancer_test.ply")
                        print("Saved: dancer_test.ply")
                    else:
                        print(f"Invalid bone '{bone_name}' or axis '{axis}'")
                except ValueError:
                    print("Invalid value")

            elif action == 'adj' and len(parts) >= 4:
                bone_name = parts[1]
                axis = parts[2].lower()
                try:
                    delta = float(parts[3])
                    if bone_name in self.bone_labels and axis in ['x', 'y', 'z']:
                        new_val = self.adjust_bone_rotation(bone_name, axis, delta)
                        print(f"Adjusted {bone_name} {axis} = {new_val}°")
                        # Auto-save
                        vertices, faces, _, _ = self.generate_mesh_and_joints()
                        mesh = trimesh.Trimesh(vertices=vertices, faces=faces, process=False)
                        mesh.export("dancer_test.ply")
                        print("Saved: dancer_test.ply")
                    else:
                        print(f"Invalid bone '{bone_name}' or axis '{axis}'")
                except ValueError:
                    print("Invalid delta")

            elif action == 'view':
                vertices, faces, bone_heads, bone_tails = self.generate_mesh_and_joints()
                self.visualize(vertices, faces, bone_heads, bone_tails)

            else:
                print("Unknown command. Type 'quit' to exit.")

    def visualize(self, vertices, faces, bone_heads, bone_tails):
        """Visualize mesh with joints using available library."""
        if HAS_PYVISTA:
            self.visualize_pyvista(vertices, faces, bone_heads, bone_tails)
        elif HAS_OPEN3D:
            self.visualize_open3d(vertices, faces, bone_heads, bone_tails)
        else:
            print("No visualization library available. Install pyvista or open3d.")
            print("  pip install pyvista")
            print("  pip install open3d")

    def visualize_pyvista(self, vertices, faces, bone_heads, bone_tails):
        """Visualize using PyVista."""
        # Create mesh
        faces_pv = np.hstack([[3] + list(f) for f in faces]).astype(np.int64)
        mesh = pv.PolyData(vertices, faces_pv)

        # Create joint points
        joint_points = pv.PolyData(bone_heads)

        # Create bone lines
        lines = []
        for i, bone_name in enumerate(self.bone_labels):
            if bone_name in self.key_bones:
                lines.append([bone_heads[i], bone_tails[i]])

        # Plot
        plotter = pv.Plotter()
        plotter.add_mesh(mesh, color='lightgray', opacity=0.7)
        plotter.add_points(joint_points, color='red', point_size=10, render_points_as_spheres=True)

        for line in lines:
            plotter.add_lines(np.array(line), color='blue', width=3)

        plotter.add_axes()
        plotter.show()

    def visualize_open3d(self, vertices, faces, bone_heads, bone_tails):
        """Visualize using Open3D."""
        # Create mesh
        mesh = o3d.geometry.TriangleMesh()
        mesh.vertices = o3d.utility.Vector3dVector(vertices)
        mesh.triangles = o3d.utility.Vector3iVector(faces)
        mesh.compute_vertex_normals()
        mesh.paint_uniform_color([0.7, 0.7, 0.7])

        # Create joint spheres
        geometries = [mesh]
        for i, bone_name in enumerate(self.bone_labels):
            if bone_name in self.key_bones:
                sphere = o3d.geometry.TriangleMesh.create_sphere(radius=0.01)
                sphere.translate(bone_heads[i])
                sphere.paint_uniform_color([1, 0, 0])
                geometries.append(sphere)

        o3d.visualization.draw_geometries(geometries)


def main():
    parser = argparse.ArgumentParser(description="Interactive Pose Adjuster")
    parser.add_argument("--view", action="store_true", help="Open 3D viewer")
    args = parser.parse_args()

    adjuster = PoseAdjuster()

    if args.view:
        vertices, faces, bone_heads, bone_tails = adjuster.generate_mesh_and_joints()
        adjuster.visualize(vertices, faces, bone_heads, bone_tails)
    else:
        adjuster.run_interactive_cli()


if __name__ == "__main__":
    main()
