#!/usr/bin/env python3
"""
Inverse Kinematics Solver for ANNY

Given target joint positions (e.g., from SAM-3D), compute the bone rotations
needed to match those positions in ANNY.

Key learnings applied:
1. Work hierarchically from root to leaf
2. Use parent bones (pelvis.R) to orient limb chains
3. Convert between coordinate systems
4. Account for bone sensitivity differences
"""

import numpy as np
import torch
import trimesh
from scipy.spatial.transform import Rotation
from anny import create_fullbody_model
from typing import Dict, Tuple, Optional
import argparse


class IKSolver:
    """Inverse Kinematics solver for ANNY model."""

    # Bone chains for IK solving (root to leaf order)
    BONE_CHAINS = {
        'right_leg': ['pelvis.R', 'upperleg01.R', 'lowerleg01.R', 'foot.R'],
        'left_leg': ['pelvis.L', 'upperleg01.L', 'lowerleg01.L', 'foot.L'],
        'right_arm': ['clavicle.R', 'shoulder01.R', 'upperarm01.R', 'lowerarm01.R', 'wrist.R'],
        'left_arm': ['clavicle.L', 'shoulder01.L', 'upperarm01.L', 'lowerarm01.L', 'wrist.L'],
        'spine': ['root', 'spine03', 'spine02', 'spine01', 'neck01', 'head'],
    }

    # Mapping from our joint names to ANNY bone names
    JOINT_TO_BONE = {
        'pelvis': 'root',
        'hip_r': 'pelvis.R',       # pelvis.R controls right hip orientation
        'hip_l': 'pelvis.L',
        'knee_r': 'upperleg01.R',  # upperleg controls knee position
        'knee_l': 'upperleg01.L',
        'ankle_r': 'lowerleg01.R',
        'ankle_l': 'lowerleg01.L',
        'foot_r': 'foot.R',
        'foot_l': 'foot.L',
        'shoulder_r': 'upperarm01.R',
        'shoulder_l': 'upperarm01.L',
        'elbow_r': 'lowerarm01.R',
        'elbow_l': 'lowerarm01.L',
        'wrist_r': 'wrist.R',
        'wrist_l': 'wrist.L',
        'neck': 'neck01',
        'head': 'head',
    }

    # Coordinate system conversion: SAM-3D to ANNY
    # SAM-3D: +X = right, ANNY: +X = left
    # Both: +Z = up
    COORD_FLIP = np.array([-1, 1, 1])  # Flip X axis

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
        self.bone_labels = list(self.model.bone_labels)

        self.phenotypes = {
            "gender": torch.tensor([[1.0]]),
            "age": torch.tensor([[0.5]]),
            "height": torch.tensor([[0.5]]),
            "weight": torch.tensor([[0.5]]),
            "muscle": torch.tensor([[0.5]]),
            "proportions": torch.tensor([[0.5]]),
        }

        # Get rest pose joint positions
        self.rest_bone_heads, self.rest_bone_tails = self._get_rest_pose_joints()

        print(f"Loaded {self.num_bones} bones")

    def _get_rest_pose_joints(self) -> Tuple[np.ndarray, np.ndarray]:
        """Get bone head/tail positions in rest (T-pose)."""
        pose_params = torch.eye(4).unsqueeze(0).unsqueeze(0).repeat(1, self.num_bones, 1, 1)

        output = self.model(
            pose_parameters=pose_params,
            phenotype_kwargs=self.phenotypes,
            pose_parameterization="rest_relative",
            return_bone_ends=True,
        )

        bone_heads = output["bone_heads"][0].detach().cpu().numpy()
        bone_tails = output["bone_tails"][0].detach().cpu().numpy()

        return bone_heads, bone_tails

    def get_bone_idx(self, name: str) -> int:
        return self.bone_labels.index(name)

    def get_rest_bone_direction(self, bone_name: str) -> np.ndarray:
        """Get the direction vector of a bone in rest pose."""
        idx = self.get_bone_idx(bone_name)
        head = self.rest_bone_heads[idx]
        tail = self.rest_bone_tails[idx]
        direction = tail - head
        length = np.linalg.norm(direction)
        if length > 1e-6:
            return direction / length
        return np.array([0, 0, 1])

    def load_sam3d_joints(self, mesh_path: str) -> Dict[str, np.ndarray]:
        """
        Load joint positions from SAM-3D mesh.

        For now, this extracts joints by analyzing the mesh geometry.
        In practice, SAM-3D may provide joint positions directly.
        """
        mesh = trimesh.load(mesh_path)
        vertices = np.array(mesh.vertices)

        # Simple joint extraction based on mesh analysis
        # This is a placeholder - should use actual SAM-3D joint output
        joints = self._extract_joints_from_mesh(vertices)

        # Convert to ANNY coordinate system
        for name, pos in joints.items():
            joints[name] = pos * self.COORD_FLIP

        return joints

    def _extract_joints_from_mesh(self, vertices: np.ndarray) -> Dict[str, np.ndarray]:
        """
        Extract approximate joint positions from mesh vertices.

        This is a simplified version - actual implementation should use
        SAM-3D's joint output or more sophisticated analysis.
        """
        # Get bounding box
        min_coords = vertices.min(axis=0)
        max_coords = vertices.max(axis=0)
        center = (min_coords + max_coords) / 2

        # Height-based landmarks
        z_coords = vertices[:, 2]
        height = max_coords[2] - min_coords[2]

        joints = {}

        # Pelvis - center at ~55% height
        pelvis_z = min_coords[2] + height * 0.55
        pelvis_mask = np.abs(z_coords - pelvis_z) < height * 0.05
        if pelvis_mask.sum() > 0:
            joints['pelvis'] = np.array([center[0], center[1], pelvis_z])

        # This is very approximate - in practice use SAM-3D joint output
        # Just returning pelvis for now as placeholder
        return joints

    def compute_rotation_between_vectors(self, v_from: np.ndarray, v_to: np.ndarray) -> np.ndarray:
        """
        Compute rotation matrix that rotates v_from to align with v_to.
        """
        v_from = v_from / (np.linalg.norm(v_from) + 1e-8)
        v_to = v_to / (np.linalg.norm(v_to) + 1e-8)

        # Cross product gives rotation axis
        cross = np.cross(v_from, v_to)
        cross_norm = np.linalg.norm(cross)

        if cross_norm < 1e-6:
            # Vectors are parallel
            dot = np.dot(v_from, v_to)
            if dot > 0:
                return np.eye(3)  # Same direction
            else:
                # Opposite direction - rotate 180° around any perpendicular axis
                perp = np.array([1, 0, 0]) if abs(v_from[0]) < 0.9 else np.array([0, 1, 0])
                axis = np.cross(v_from, perp)
                axis = axis / np.linalg.norm(axis)
                return Rotation.from_rotvec(np.pi * axis).as_matrix()

        axis = cross / cross_norm
        angle = np.arccos(np.clip(np.dot(v_from, v_to), -1, 1))

        return Rotation.from_rotvec(angle * axis).as_matrix()

    def world_to_local_rotation(self, world_rot: np.ndarray, parent_world_rot: np.ndarray) -> np.ndarray:
        """
        Convert a world-space rotation to local (bone-relative) rotation.

        local_rot = parent_world_rot^T @ world_rot
        """
        return parent_world_rot.T @ world_rot

    def compute_chain_ik(
        self,
        chain_name: str,
        target_positions: Dict[str, np.ndarray],
        iterations: int = 10
    ) -> Dict[str, np.ndarray]:
        """
        Compute IK for a bone chain given target joint positions.

        Uses a simple iterative approach:
        1. For each bone (root to leaf):
           - Compute target direction to next joint
           - Compute rotation to align bone with target
           - Apply rotation and propagate to children

        Args:
            chain_name: Name of chain ('right_leg', 'left_arm', etc.)
            target_positions: Dict mapping joint names to target 3D positions
            iterations: Number of IK iterations

        Returns:
            Dict mapping bone names to 4x4 rotation matrices
        """
        chain = self.BONE_CHAINS.get(chain_name, [])
        if not chain:
            print(f"Unknown chain: {chain_name}")
            return {}

        rotations = {}

        for bone_name in chain:
            rotations[bone_name] = np.eye(4)

        # Simple one-pass IK (can be made iterative for better results)
        for i, bone_name in enumerate(chain[:-1]):  # Skip last bone (end effector)
            next_bone = chain[i + 1]

            # Get current bone direction in rest pose
            rest_dir = self.get_rest_bone_direction(bone_name)

            # Get target direction (if we have target positions for adjacent joints)
            # This is simplified - full IK would track accumulated transforms
            bone_idx = self.get_bone_idx(bone_name)
            next_idx = self.get_bone_idx(next_bone)

            current_head = self.rest_bone_heads[bone_idx]
            current_tail = self.rest_bone_tails[bone_idx]

            # For now, just use rest direction as target (placeholder)
            # In full implementation, would compute from target_positions
            target_dir = rest_dir

            # Compute rotation
            rot_mat = self.compute_rotation_between_vectors(rest_dir, target_dir)

            # Store as 4x4 matrix
            rot_4x4 = np.eye(4)
            rot_4x4[:3, :3] = rot_mat
            rotations[bone_name] = rot_4x4

        return rotations

    def solve_from_target_joints(
        self,
        target_joints: Dict[str, np.ndarray]
    ) -> Dict[str, Dict[str, float]]:
        """
        Main IK solver: given target joint positions, compute bone rotations.

        Args:
            target_joints: Dict mapping joint names to 3D positions
                         e.g., {'hip_r': [x, y, z], 'knee_r': [x, y, z], ...}

        Returns:
            Dict mapping bone names to rotation dict {'x': deg, 'y': deg, 'z': deg}
        """
        pose_rotations = {}

        # Process each limb chain
        for chain_name, chain_bones in self.BONE_CHAINS.items():
            # Get relevant target joints for this chain
            chain_targets = {}
            for joint_name, pos in target_joints.items():
                if self.JOINT_TO_BONE.get(joint_name) in chain_bones:
                    chain_targets[joint_name] = pos

            if chain_targets:
                chain_rots = self.compute_chain_ik(chain_name, chain_targets)

                # Convert rotation matrices to Euler angles
                for bone_name, rot_4x4 in chain_rots.items():
                    rot_3x3 = rot_4x4[:3, :3]
                    euler = Rotation.from_matrix(rot_3x3).as_euler('xyz', degrees=True)
                    pose_rotations[bone_name] = {
                        'x': float(euler[0]),
                        'y': float(euler[1]),
                        'z': float(euler[2])
                    }

        return pose_rotations

    def generate_posed_mesh(
        self,
        pose_rotations: Dict[str, Dict[str, float]],
        output_path: Optional[str] = None
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Generate mesh with given pose rotations."""
        pose_params = torch.eye(4).unsqueeze(0).unsqueeze(0).repeat(1, self.num_bones, 1, 1)

        for bone_name, rot_dict in pose_rotations.items():
            if bone_name in self.bone_labels:
                idx = self.get_bone_idx(bone_name)
                euler = [rot_dict.get('x', 0), rot_dict.get('y', 0), rot_dict.get('z', 0)]
                rot = Rotation.from_euler('xyz', euler, degrees=True)
                mat = np.eye(4)
                mat[:3, :3] = rot.as_matrix()
                pose_params[0, idx] = torch.from_numpy(mat).float()

        output = self.model(
            pose_parameters=pose_params,
            phenotype_kwargs=self.phenotypes,
            pose_parameterization="rest_relative",
        )

        vertices = output["vertices"][0].detach().cpu().numpy()
        faces = self.model.get_triangular_faces().cpu().numpy()

        if output_path:
            mesh = trimesh.Trimesh(vertices=vertices, faces=faces, process=False)
            mesh.export(output_path)
            print(f"Saved: {output_path}")

        return vertices, faces

    def print_joint_comparison(
        self,
        target_joints: Dict[str, np.ndarray],
        current_joints: Dict[str, np.ndarray]
    ):
        """Print comparison between target and current joint positions."""
        print("\n=== Joint Position Comparison ===")
        print(f"{'Joint':<15} {'Target X':>8} {'Target Y':>8} {'Target Z':>8} | "
              f"{'Current X':>8} {'Current Y':>8} {'Current Z':>8} | {'Error':>8}")
        print("-" * 100)

        for joint_name in sorted(target_joints.keys()):
            if joint_name in current_joints:
                target = target_joints[joint_name]
                current = current_joints[joint_name]
                error = np.linalg.norm(target - current)
                print(f"{joint_name:<15} {target[0]:>8.3f} {target[1]:>8.3f} {target[2]:>8.3f} | "
                      f"{current[0]:>8.3f} {current[1]:>8.3f} {current[2]:>8.3f} | {error:>8.3f}")


def main():
    parser = argparse.ArgumentParser(description="IK Solver for ANNY")
    parser.add_argument("--mesh", type=str, help="SAM-3D mesh to extract joints from")
    parser.add_argument("--output", type=str, default="ik_result.ply", help="Output mesh path")
    args = parser.parse_args()

    solver = IKSolver()

    # Example: manually specify target joint positions (in ANNY coordinates)
    # These would normally come from SAM-3D
    print("\n=== Example: Dancer Pose Target ===")

    # Based on empirical findings for dancer pose leg:
    # pelvis.R: x=5, y=-60
    # upperleg01.R: x=-5
    # lowerleg01.R: x=50

    # We can work backwards to see what joint positions those rotations produce
    test_rotations = {
        'pelvis.R': {'x': 5, 'y': -60, 'z': 0},
        'upperleg01.R': {'x': -5, 'y': 0, 'z': 0},
        'lowerleg01.R': {'x': 50, 'y': 0, 'z': 0},
    }

    print("\nGenerating mesh with known good rotations...")
    solver.generate_posed_mesh(test_rotations, "dancer_leg_reference.ply")

    print("\n=== Rotation Parameters ===")
    for bone, rots in test_rotations.items():
        parts = []
        for axis in ['x', 'y', 'z']:
            if rots[axis] != 0:
                parts.append(f"rotation_{axis}({rots[axis]})")
        if parts:
            print(f'"{bone}": {" @ ".join(parts)}')


if __name__ == "__main__":
    main()
