import numpy as np
from scipy.spatial.transform import Rotation

class ANNYPoseSolver:
    """
    Solves for ANNY pose parameters to match target joint positions.
    Uses hierarchical analytic IK (chain-by-chain vector alignment).
    """

    def __init__(self, bone_labels: list[str]):
        self.bone_labels = bone_labels
        self.bone_indices = {name: i for i, name in enumerate(bone_labels)}

    def compute_pose(
        self,
        source_joints: dict[str, np.ndarray],
        target_joints: dict[str, np.ndarray],
        rest_bone_poses: np.ndarray,
    ) -> dict[str, np.ndarray]:
        """
        Compute bone rotations to align source_joints (rest) to target_joints (SAM-3D).
        
        This solves the "Head Alignment" problem by treating the spine/neck/head 
        as a kinematic chain. Instead of manually offsetting the head position, 
        the solver finds the neck rotation required to point the ANNY neck bone 
        towards the SAM-3D head position. This naturally handles anterior/posterior 
        head carriage differences.

        Args:
            source_joints: Dictionary of joint positions in ANNY rest pose (T-pose).
            target_joints: Dictionary of target joint positions (from SAM-3D).
            rest_bone_poses: (J, 4, 4) Global transform matrices of bones in rest pose.

        Returns:
            Dictionary of {bone_name: rotvec} representing local rotations relative to rest pose.
        """
        rotations = {}
        world_rotations = {} # Stores global rotation delta for each bone (to pass to children)

        # Define kinematic chains (Parent -> Child)
        # Structure: (StartJoint, EndJoint, BoneName, ParentBoneName)
        chains = [
            # --- SPINE / HEAD CHAIN ---
            # Rotates neck to point to head. Handles head offset naturally.
            ("neck", "head", "neck01", None), 

            # --- LEFT ARM ---
            ("shoulder_l", "elbow_l", "upperarm01.L", None),
            ("elbow_l", "wrist_l", "lowerarm01.L", "upperarm01.L"),

            # --- RIGHT ARM ---
            ("shoulder_r", "elbow_r", "upperarm01.R", None),
            ("elbow_r", "wrist_r", "lowerarm01.R", "upperarm01.R"),

            # --- LEFT LEG ---
            ("hip_l", "knee_l", "upperleg01.L", None),
            ("knee_l", "ankle_l", "lowerleg01.L", "upperleg01.L"),

            # --- RIGHT LEG ---
            ("hip_r", "knee_r", "upperleg01.R", None),
            ("knee_r", "ankle_r", "lowerleg01.R", "upperleg01.R"),
        ]

        # 1. Global Root Alignment (Pelvis/Hips)
        # Align global heading (yaw)
        self._solve_root_heading(rotations, source_joints, target_joints)

        # 2. Hierarchical Chain Solving
        for start, end, bone_name, parent_bone in chains:
            if start not in source_joints or end not in source_joints:
                continue
            if start not in target_joints or end not in target_joints:
                continue

            # A. Get vectors
            src_vec = source_joints[end] - source_joints[start]
            src_dir = src_vec / (np.linalg.norm(src_vec) + 1e-8)

            tgt_vec = target_joints[end] - target_joints[start]
            tgt_dir = tgt_vec / (np.linalg.norm(tgt_vec) + 1e-8)

            # B. Get Parent's Global Delta Rotation
            # If parent rotated, the child's "rest" vector has already moved.
            if parent_bone and parent_bone in world_rotations:
                R_parent_delta = world_rotations[parent_bone]
                current_dir = R_parent_delta @ src_dir
            else:
                R_parent_delta = np.eye(3)
                current_dir = src_dir

            # C. Solve for Local Delta Rotation (R_local)
            # Find R_local such that: R_local @ current_dir = tgt_dir
            axis = np.cross(current_dir, tgt_dir)
            axis_norm = np.linalg.norm(axis)
            
            if axis_norm < 1e-6:
                # Aligned or opposite
                dot = np.dot(current_dir, tgt_dir)
                if dot > 0: # Aligned
                    R_local_delta = np.eye(3)
                    local_rotvec_global = np.zeros(3)
                else: # Opposite (180 deg flip) - rare for limbs
                    # Rotate 180 around any orthogonal axis
                    ortho = np.cross(current_dir, np.array([1,0,0]))
                    if np.linalg.norm(ortho) < 1e-6: ortho = np.cross(current_dir, np.array([0,1,0]))
                    ortho /= np.linalg.norm(ortho)
                    R_local_delta = Rotation.from_rotvec(ortho * np.pi).as_matrix()
                    local_rotvec_global = ortho * np.pi
            else:
                axis = axis / axis_norm
                angle = np.arccos(np.clip(np.dot(current_dir, tgt_dir), -1, 1))
                local_rotvec_global = axis * angle
                R_local_delta = Rotation.from_rotvec(local_rotvec_global).as_matrix()

            # D. Store Total World Delta for Children
            # Next child starts from this new orientation
            world_rotations[bone_name] = R_local_delta @ R_parent_delta

            # E. Convert to Bone Local Space (for ANNY parameter)
            # ANNY expects rotation relative to the bone's REST frame.
            # We calculated `local_rotvec_global` which is a rotation in Global Space.
            # Transform: v_local = R_rest.T @ v_global
            
            if bone_name in self.bone_indices:
                idx = self.bone_indices[bone_name]
                rest_global_rot = rest_bone_poses[idx, :3, :3]
                
                # Transform the rotation matrix into the local frame of the bone
                # R_param = R_rest.T @ R_local_delta @ R_rest
                # This expresses the "global delta" as a "local delta"
                local_mat = rest_global_rot.T @ R_local_delta @ rest_global_rot
                
                final_rotvec = Rotation.from_matrix(local_mat).as_rotvec()
                
                # Apply heuristic scaling/damping if needed (e.g. for twists)
                final_rotvec = self._apply_heuristics(bone_name, final_rotvec)
                
                rotations[bone_name] = final_rotvec

        return rotations

    def _solve_root_heading(self, rotations, src, tgt):
        """Align root yaw (heading) based on hips."""
        if 'hip_l' not in src or 'hip_r' not in src: return
        if 'hip_l' not in tgt or 'hip_r' not in tgt: return

        # Vector Left->Right (or Right->Left)
        src_vec = src['hip_l'] - src['hip_r']
        tgt_vec = tgt['hip_l'] - tgt['hip_r']
        
        # Angle in XY plane (Z-up)
        src_angle = np.arctan2(src_vec[1], src_vec[0])
        tgt_angle = np.arctan2(tgt_vec[1], tgt_vec[0])
        
        diff = tgt_angle - src_angle
        
        # Set root rotation (global Z)
        rotations['root'] = np.array([0, 0, diff])

    def _apply_heuristics(self, bone_name: str, rotvec: np.ndarray) -> np.ndarray:
        """Apply empirical scaling/damping to rotations."""
        # Decompose components
        # Note: This assumes bone local axes align with anatomy in a specific way.
        # ANNY default rig: 
        #   UpperLeg: X=Flexion/Extension, Y=Twist, Z=Abduction
        
        if "upperleg" in bone_name.lower() or "lowerleg" in bone_name.lower():
             # Legs: Damping twist (Y) and Abduction (Z) often helps stability
             return np.array([
                 rotvec[0],       # Keep flexion fully
                 rotvec[1] * 0.5, # Dampen twist
                 rotvec[2] * 0.5  # Dampen abduction
             ])
        
        return rotvec
