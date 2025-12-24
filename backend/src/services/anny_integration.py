"""ANNY integration for body mesh fitting and measurement extraction.

This module integrates with NAVER's ANNY body model to:
1. Fit ANNY phenotype parameters to SAM-3D-Body mesh output
2. Extract semantic body measurements (height, waist, bust, hips)
3. Classify body type from measurements
"""

import io
from dataclasses import dataclass

import httpx
import numpy as np
import trimesh
from scipy.spatial import cKDTree
from services.anny_pose_solver import ANNYPoseSolver

# ANNY imports - requires anny package installed
try:
    import torch
    from anny import Anthropometry, create_fullbody_model
    from anny.parameters_regressor import ParametersRegressor

    ANNY_AVAILABLE = True
except ImportError:
    ANNY_AVAILABLE = False
    torch = None
    ParametersRegressor = None


@dataclass
class BodyMeasurements:
    """Body measurements extracted from fitted ANNY model."""

    height_cm: float
    bust_cm: float
    waist_cm: float
    hips_cm: float
    weight_kg: float
    bmi: float

    # Fitted phenotype parameters (0-1 scale)
    gender_param: float  # 0=male, 1=female
    age_param: float
    muscle_param: float
    weight_param: float


@dataclass
class FittingResult:
    """Result from ANNY fitting to SAM-3D mesh."""

    measurements: BodyMeasurements
    phenotypes: dict[str, float]
    fitted_vertices: np.ndarray
    confidence: float


class ANNYBodyAnalyzer:
    """
    Analyzes body measurements by fitting ANNY phenotypes to SAM-3D-Body mesh output.

    Workflow:
    1. Download PLY mesh from SAM-3D-Body URL
    2. Transform coordinates (SAM-3D is Y-up, ANNY is Z-up)
    3. Fit ANNY phenotype parameters via grid search
    4. Extract semantic measurements from fitted ANNY model
    """

    def __init__(
        self,
        device: str = None,
        dtype=None,
    ):
        """
        Initialize the ANNY body analyzer.

        Args:
            device: Torch device ('cuda' or 'cpu'). Auto-detected if None.
            dtype: Torch dtype for computations
        """
        if not ANNY_AVAILABLE:
            raise ImportError(
                "ANNY package not installed. Install from: "
                "https://github.com/naver/anny"
            )

        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.dtype = dtype or torch.float32
        self._model = None
        self._anthropometry = None
        self._regressor = None

    def _ensure_model_loaded(self) -> None:
        """Lazy load ANNY model."""
        if self._model is not None:
            return

        # Create ANNY full body model
        self._model = create_fullbody_model(
            rig="default",
            topology="default",
            remove_unattached_vertices=True,
            triangulate_faces=True,
        )
        self._model = self._model.to(device=self.device, dtype=self.dtype)

        # Create anthropometry for measurements
        self._anthropometry = Anthropometry(self._model)

    def _ensure_regressor_loaded(self) -> None:
        """Lazy load ParametersRegressor for hierarchical fitting."""
        self._ensure_model_loaded()
        if self._regressor is not None:
            return

        # Regularization weights control how much each phenotype can change
        # Lower weight = more freedom to optimize, Higher weight = more constrained
        # ANNY phenotypes: gender, age, muscle, weight, height, proportions
        reg_weights = {
            "gender": 100.0,  # Freeze if known from user input
            "age": 10.0,  # Age has subtle effects, keep stable
            "height": 100.0,  # Freeze - we know this from user input
            "weight": 0.5,  # Allow weight to vary freely
            "muscle": 5.0,  # Higher constraint - prevent extreme muscle
            "proportions": 2.0,  # Moderate constraint
        }

        self._regressor = ParametersRegressor(
            self._model,
            verbose=False,
            max_n_iters=5,
            reg_weight_kwargs=reg_weights,
        )

    def _extract_skeletal_landmarks(
        self,
        mesh: trimesh.Trimesh,
    ) -> dict[str, np.ndarray]:
        """
        Phase 1: Extract skeletal landmarks from SAM-3D mesh.

        Finds anatomical positions by scanning the mesh geometry:
        - Pelvis center: centroid at hip level
        - Shoulder level: where arms split from torso
        - Torso proportions: bust/waist/hip ratios

        Args:
            mesh: SAM-3D mesh (Z-up, centered)

        Returns:
            Dictionary of landmark positions and measurements
        """
        verts = mesh.vertices
        min_z = verts[:, 2].min()
        max_z = verts[:, 2].max()
        height = max_z - min_z

        landmarks = {
            "height": height,
            "min_z": min_z,
            "max_z": max_z,
        }

        # Find pelvis center (around 52-55% height)
        pelvis_z = min_z + height * 0.53
        pelvis_slice = mesh.section(plane_normal=[0, 0, 1], plane_origin=[0, 0, pelvis_z])
        if pelvis_slice and pelvis_slice.discrete:
            # Find the largest loop (torso, not legs)
            largest_loop = max(pelvis_slice.discrete, key=lambda l: len(l))
            pelvis_center = largest_loop[:, :2].mean(axis=0)
            landmarks["pelvis_center"] = np.array([pelvis_center[0], pelvis_center[1], pelvis_z])

        # Find shoulder level (where arms split - transition from 1 to 3+ loops)
        for pct in range(80, 65, -2):
            z = min_z + height * (pct / 100)
            path = mesh.section(plane_normal=[0, 0, 1], plane_origin=[0, 0, z])
            if path and path.discrete and len(path.discrete) >= 3:
                landmarks["shoulder_z"] = z
                break
        else:
            landmarks["shoulder_z"] = min_z + height * 0.73

        # Measure circumferences at key levels for volume estimation
        circumferences = {}
        for name, pct in [("bust", 0.72), ("waist", 0.62), ("hips", 0.53)]:
            z = min_z + height * pct
            path = mesh.section(plane_normal=[0, 0, 1], plane_origin=[0, 0, z])
            if path and path.discrete:
                # Use largest loop for body (not arms)
                perims = []
                for loop in path.discrete:
                    if len(loop) >= 3:
                        perim = sum(
                            np.linalg.norm(loop[i] - loop[(i + 1) % len(loop)])
                            for i in range(len(loop))
                        )
                        perims.append(perim)
                if perims:
                    circumferences[name] = max(perims)

        landmarks["circumferences"] = circumferences

        # Estimate mesh volume (for weight phenotype estimation)
        try:
            if mesh.is_watertight:
                landmarks["volume"] = mesh.volume
            else:
                landmarks["volume"] = mesh.convex_hull.volume * 0.85  # Rough estimate
        except Exception:
            landmarks["volume"] = None

        return landmarks

    def _extract_joint_positions(
        self,
        mesh: trimesh.Trimesh,
    ) -> dict[str, np.ndarray]:
        """
        Extract 3D joint positions from mesh by analyzing limb geometry.

        Segments the mesh into body parts and finds joint positions:
        - Pelvis: center of torso at hip level
        - Shoulders: where arms split from torso (left/right)
        - Elbows: middle of arm tubes
        - Wrists: end of arm tubes
        - Hips: left/right at crotch level
        - Knees: middle of leg tubes
        - Ankles: end of leg tubes

        Args:
            mesh: SAM-3D mesh (Z-up, centered)

        Returns:
            Dictionary of joint names to 3D positions
        """
        verts = mesh.vertices
        min_z = verts[:, 2].min()
        max_z = verts[:, 2].max()
        height = max_z - min_z

        joints = {}

        # Helper: get loop centers at a given height
        def get_loops_at_height(z: float) -> list[np.ndarray]:
            """Return list of loop centers (x, y, z) at given height."""
            path = mesh.section(plane_normal=[0, 0, 1], plane_origin=[0, 0, z])
            if not path or not path.discrete:
                return []
            centers = []
            for loop in path.discrete:
                if len(loop) >= 3:
                    cx, cy = loop[:, 0].mean(), loop[:, 1].mean()
                    centers.append(np.array([cx, cy, z]))
            return centers

        # Helper: find left/right loops (by x-coordinate)
        def split_left_right(centers: list[np.ndarray]) -> tuple[np.ndarray | None, np.ndarray | None]:
            """Split loops into left (negative x) and right (positive x)."""
            if not centers:
                return None, None
            left = [c for c in centers if c[0] < 0]
            right = [c for c in centers if c[0] >= 0]
            left_center = np.mean(left, axis=0) if left else None
            right_center = np.mean(right, axis=0) if right else None
            return left_center, right_center

        # ===== SHOULDERS (find first to track arms) =====
        # Where arms split from torso - find the 3-loop level
        shoulder_z = min_z + height * 0.80
        for pct in range(82, 68, -1):
            z = min_z + height * (pct / 100)
            loops = get_loops_at_height(z)
            if len(loops) >= 3:
                shoulder_z = z
                # Shoulders are the non-central loops
                torso = min(loops, key=lambda c: abs(c[0]) + abs(c[1]))  # Most central
                arms = [c for c in loops if not np.allclose(c, torso)]
                left, right = split_left_right(arms)
                if left is not None:
                    joints["shoulder_l"] = np.array([left[0], left[1], z])
                if right is not None:
                    joints["shoulder_r"] = np.array([right[0], right[1], z])
                break

        # ===== ELBOWS (track arms down from shoulders) =====
        # Scan down from shoulders to find arm loops
        arm_positions = {"l": [], "r": []}  # Track arm positions for later exclusion

        if "shoulder_l" in joints:
            arm_positions["l"].append(joints["shoulder_l"][:2])
        if "shoulder_r" in joints:
            arm_positions["r"].append(joints["shoulder_r"][:2])

        if "shoulder_l" in joints or "shoulder_r" in joints:
            shoulder_z = joints.get("shoulder_l", joints.get("shoulder_r"))[2]
            for pct_offset in range(5, 25, 2):
                z = shoulder_z - height * (pct_offset / 100)
                if z < min_z + height * 0.45:
                    break
                loops = get_loops_at_height(z)
                # Look for small loops (arms) away from center
                arm_loops = [c for c in loops if abs(c[0]) > 0.05]  # Not torso
                if len(arm_loops) >= 2:
                    left, right = split_left_right(arm_loops)
                    if left is not None and "elbow_l" not in joints:
                        joints["elbow_l"] = left
                        arm_positions["l"].append(left[:2])
                    if right is not None and "elbow_r" not in joints:
                        joints["elbow_r"] = right
                        arm_positions["r"].append(right[:2])
                    if "elbow_l" in joints and "elbow_r" in joints:
                        break

        # ===== WRISTS (continue tracking arms) =====
        # Track each arm separately based on proximity to elbow
        for side, elbow_key, wrist_key in [("l", "elbow_l", "wrist_l"), ("r", "elbow_r", "wrist_r")]:
            if elbow_key not in joints:
                continue
            elbow_pos = joints[elbow_key]
            last_arm_pos = elbow_pos.copy()

            for pct_offset in range(5, 35, 2):
                z = elbow_pos[2] - height * (pct_offset / 100)
                if z < min_z + height * 0.20:
                    break
                loops = get_loops_at_height(z)
                if not loops:
                    continue

                # Find loop closest to last known arm position
                best_loop = None
                best_dist = float('inf')
                for loop in loops:
                    # Skip torso (too central)
                    if abs(loop[0]) < 0.03 and abs(loop[1]) < 0.1:
                        continue
                    dist = np.linalg.norm(loop[:2] - last_arm_pos[:2])
                    if dist < best_dist and dist < 0.15:
                        best_dist = dist
                        best_loop = loop

                if best_loop is not None:
                    last_arm_pos = best_loop
                    joints[wrist_key] = best_loop
                    arm_positions[side].append(best_loop[:2])

        # Helper: check if a loop is near any tracked arm position
        def is_near_arm(loop_center: np.ndarray, threshold: float = 0.08) -> bool:
            """Check if loop is close to any tracked arm position."""
            for side in ["l", "r"]:
                for arm_pos in arm_positions[side]:
                    dist = np.linalg.norm(loop_center[:2] - arm_pos)
                    if dist < threshold:
                        return True
            return False

        # ===== PELVIS =====
        # Center of torso at crotch level (~48% height, where legs merge)
        for pct in range(52, 44, -1):
            z = min_z + height * (pct / 100)
            loops = get_loops_at_height(z)
            # Filter out arm loops
            body_loops = [c for c in loops if not is_near_arm(c)]
            if len(body_loops) == 1:  # Single torso loop (legs have merged)
                joints["pelvis"] = body_loops[0]
                break
            elif len(body_loops) >= 2:
                # If we have 2+ loops (legs), pelvis is between them
                all_centers = np.array(body_loops)
                joints["pelvis"] = np.mean(all_centers, axis=0)
                joints["pelvis"][2] = z
                break
        if "pelvis" not in joints:
            z = min_z + height * 0.50
            hip_mask = np.abs(verts[:, 2] - z) < height * 0.05
            if hip_mask.sum() > 0:
                hip_verts = verts[hip_mask]
                joints["pelvis"] = np.mean(hip_verts, axis=0)
            else:
                joints["pelvis"] = np.array([0, 0, z])

        # ===== HIPS (left/right) =====
        # Just below where legs split (~46% height)
        # EXCLUDE arm loops using tracked positions
        for pct in range(48, 40, -1):
            z = min_z + height * (pct / 100)
            loops = get_loops_at_height(z)
            # Filter out arm loops
            leg_loops = [c for c in loops if not is_near_arm(c)]
            if len(leg_loops) >= 2:
                # Use the two loops closest to pelvis X position (legs, not arms)
                if "pelvis" in joints:
                    pelvis_x = joints["pelvis"][0]
                    # Sort by distance from pelvis X
                    leg_loops.sort(key=lambda c: abs(c[0] - pelvis_x))
                    # Take the two closest to pelvis
                    leg_loops = leg_loops[:2]
                left, right = split_left_right(leg_loops)
                if left is not None:
                    joints["hip_l"] = left
                if right is not None:
                    joints["hip_r"] = right
                break

        # ===== KNEES =====
        # Middle of thighs (~28% height)
        z = min_z + height * 0.28
        loops = get_loops_at_height(z)
        # At knee level, arms shouldn't reach this low, but filter just in case
        leg_loops = [c for c in loops if not is_near_arm(c)]
        if len(leg_loops) >= 2:
            left, right = split_left_right(leg_loops)
            if left is not None:
                joints["knee_l"] = left
            if right is not None:
                joints["knee_r"] = right

        # ===== ANKLES =====
        # Near bottom of legs (~5% height)
        z = min_z + height * 0.05
        loops = get_loops_at_height(z)
        if len(loops) >= 2:
            left, right = split_left_right(loops)
            if left is not None:
                joints["ankle_l"] = left
            if right is not None:
                joints["ankle_r"] = right

        # ===== SPINE/NECK =====
        # Find neck at ~85% height - use actual loop center, not just z-axis
        z = min_z + height * 0.85
        loops = get_loops_at_height(z)
        if loops:
            # Find the most central loop (should be neck/torso)
            neck_loop = min(loops, key=lambda c: abs(c[0]) + abs(c[1]))
            joints["neck"] = neck_loop
        else:
            joints["neck"] = np.array([0, 0, z])

        # ===== HEAD =====
        # Find head at ~95% height - use actual loop center
        z = min_z + height * 0.95
        loops = get_loops_at_height(z)
        if loops:
            # Head should be the loop at top
            head_loop = min(loops, key=lambda c: abs(c[0]) + abs(c[1]))
            joints["head"] = head_loop
        else:
            # Fallback: use top vertex center
            top_mask = verts[:, 2] > min_z + height * 0.90
            if top_mask.sum() > 0:
                top_verts = verts[top_mask]
                joints["head"] = np.mean(top_verts, axis=0)
            else:
                joints["head"] = np.array([0, 0, z])

        return joints

    def _extract_joints_from_keypoints(
        self,
        keypoints_3d: list[list[float]],
    ) -> tuple[dict[str, np.ndarray], np.ndarray]:
        """
        Extract joints from SAM-3D 70-keypoint data in ANNY coordinate space.
        Does NOT perform centering or alignment - just coordinate transformation.

        Args:
            keypoints_3d: 70x3 array of keypoints from SAM-3D

        Returns:
            Tuple of (named_joints_dict, all_transformed_keypoints)
        """
        kp = np.array(keypoints_3d)
        
        # Transformation: SAM-3D JSON -> ANNY space
        # 1. Flip Y (JSON Y is inverted relative to PLY)
        kp_ply_space = kp.copy()
        kp_ply_space[:, 1] *= -1

        # 2. Transform to ANNY space (X, Z, Y)
        # Old X -> New X
        # Old Y (Up) -> New Z (Up)
        # Old Z (Depth) -> New Y (Forward/Back)
        kp_transformed = kp_ply_space[:, [0, 2, 1]].copy()
        # No flips needed here - pelvis alignment handles translation
        # and X/Y axes seem to match after permutation based on visual feedback

        # 3. Align Pelvis
        # Calculate current keypoint pelvis center (midpoint of hips)
        # Hips are indices 9 (right) and 10 (left)
        if len(kp_transformed) > 10:
            kp_pelvis = (kp_transformed[9] + kp_transformed[10]) / 2
        else:
            kp_pelvis = kp_transformed.mean(axis=0)

        # If no target, just center the pelvis at origin
        # (Alignment to target is now done in analyze_from_vertices via centering)
        kp_final = kp_transformed - kp_pelvis

        # Mapping based on MHR70 format (sam-3d-body/sam_3d_body/metadata/mhr70.py)
        # 0: nose
        # 1: left_eye
        # 2: right_eye
        # 3: left_ear
        # 4: right_ear
        # 5: left_shoulder
        # 6: right_shoulder
        # 7: left_elbow
        # 8: right_elbow
        # 9: left_hip
        # 10: right_hip
        # 11: left_knee
        # 12: right_knee
        # 13: left_ankle
        # 14: right_ankle
        # 15-17: left foot (big toe, small toe, heel)
        # 18-20: right foot (big toe, small toe, heel)
        # 21-40: right hand (thumb to pinky)
        # 41: right_wrist
        # 42-61: left hand (thumb to pinky)
        # 62: left_wrist
        # 63: left_olecranon
        # 64: right_olecranon
        # 65: left_cubital_fossa
        # 66: right_cubital_fossa
        # 67: left_acromion
        # 68: right_acromion
        # 69: neck

        mapping = {
            'head': 0,
            'shoulder_l': 5,  # CORRECTED: 5 is left_shoulder
            'shoulder_r': 6,  # CORRECTED: 6 is right_shoulder
            'elbow_l': 7,     # CORRECTED: 7 is left_elbow
            'elbow_r': 8,     # CORRECTED: 8 is right_elbow
            'hip_l': 9,       # CORRECTED: 9 is left_hip
            'hip_r': 10,      # CORRECTED: 10 is right_hip
            'knee_l': 11,     # CORRECTED: 11 is left_knee
            'knee_r': 12,     # CORRECTED: 12 is right_knee
            'ankle_l': 13,    # CORRECTED: 13 is left_ankle
            'ankle_r': 14,    # CORRECTED: 14 is right_ankle
            'wrist_l': 62,    # CORRECTED: 62 is left_wrist
            'wrist_r': 41,    # CORRECTED: 41 is right_wrist
            'neck': 69,       # CORRECTED: 69 is neck
            'olecranon_l': 63,
            'olecranon_r': 64,
            'acromion_l': 67,
            'acromion_r': 68,
        }

        joints = {}
        for name, idx in mapping.items():
            if idx < len(kp_final):
                joints[name] = kp_final[idx]

        # Add pelvis as midpoint of hips
        if 'hip_l' in joints and 'hip_r' in joints:
            joints['pelvis'] = (joints['hip_l'] + joints['hip_r']) / 2

        # Adjust SAM-3D head (front surface) to match ANNY head (center)
        # Move head backward by ~16cm
        if 'head' in joints:
            joints['head'][1] += 0.10

        return joints, kp_final

    def _save_all_keypoints_debug(
        self,
        keypoints: np.ndarray,
        filepath: str,
        sphere_radius: float = 0.01,
    ) -> None:
        """Save all keypoints as small spheres for alignment verification."""
        meshes = []
        for i, pos in enumerate(keypoints):
            sphere = trimesh.creation.icosphere(subdivisions=0, radius=sphere_radius)
            sphere.apply_translation(pos)
            # Rainbow colors based on index
            color = [int(x * 255) for x in trimesh.visual.color.random_color()[:3]]
            sphere.visual.vertex_colors = np.array([color + [255]] * len(sphere.vertices), dtype=np.uint8)
            meshes.append(sphere)
        
        if meshes:
            combined = trimesh.util.concatenate(meshes)
            combined.export(filepath)

    def _save_joints_debug(
        self,
        joints: dict[str, np.ndarray],
        filepath: str,
        sphere_radius: float = 0.02,
    ) -> None:
        """
        Save extracted joints as a mesh with small spheres for visualization.

        Also saves a _points.ply file with just the joint centers as vertices
        (one vertex per joint, in consistent order for easy loading).

        Args:
            joints: Dictionary of joint names to 3D positions
            filepath: Path to save the PLY file
            sphere_radius: Radius of spheres at each joint
        """
        # Standard joint order for consistent loading
        joint_order = [
            'pelvis', 'hip_l', 'hip_r', 'knee_l', 'knee_r',
            'ankle_l', 'ankle_r', 'shoulder_l', 'shoulder_r',
            'elbow_l', 'elbow_r', 'wrist_l', 'wrist_r',
            'neck', 'head'
        ]

        # Color scheme for joints (RGB 0-255)
        # Using distinct colors for easy identification
        joint_colors = {
            'pelvis': [255, 0, 0],       # Red - center/root
            'hip_l': [255, 128, 0],      # Orange - left hip
            'hip_r': [255, 64, 0],       # Dark orange - right hip
            'knee_l': [255, 255, 0],     # Yellow - left knee
            'knee_r': [200, 200, 0],     # Dark yellow - right knee
            'ankle_l': [0, 255, 0],      # Green - left ankle
            'ankle_r': [0, 200, 0],      # Dark green - right ankle
            'shoulder_l': [0, 255, 255], # Cyan - left shoulder
            'shoulder_r': [0, 200, 200], # Dark cyan - right shoulder
            'elbow_l': [0, 128, 255],    # Light blue - left elbow
            'elbow_r': [0, 64, 255],     # Blue - right elbow
            'wrist_l': [128, 0, 255],    # Purple - left wrist
            'wrist_r': [64, 0, 255],     # Dark purple - right wrist
            'neck': [255, 0, 255],       # Magenta - neck
            'head': [255, 255, 255],     # White - head
        }

        # Save sphere visualization with colors
        meshes = []
        for name, pos in joints.items():
            sphere = trimesh.creation.icosphere(subdivisions=1, radius=sphere_radius)
            sphere.apply_translation(pos)
            # Apply color to all vertices of this sphere
            color = joint_colors.get(name, [128, 128, 128])  # Gray default
            sphere.visual.vertex_colors = np.array([color + [255]] * len(sphere.vertices), dtype=np.uint8)
            meshes.append(sphere)

        if meshes:
            combined = trimesh.util.concatenate(meshes)
            combined.export(filepath)
            # Print color legend
            print(f"  Joint colors saved to {filepath}:")
            print(f"    {'Joint Name':<15} {'Color (RGB)':<20} {'Visual Description'}")
            print(f"    {'-'*15} {'-'*20} {'-'*20}")
            for name in joint_order:
                if name in joints:
                    c = joint_colors.get(name, [128, 128, 128])
                    # Add descriptive text for common colors
                    desc = ""
                    if c == [255, 0, 0]: desc = "Red"
                    elif c == [0, 255, 0]: desc = "Green"
                    elif c == [0, 0, 255]: desc = "Blue"
                    elif c == [255, 255, 0]: desc = "Yellow"
                    elif c == [0, 255, 255]: desc = "Cyan"
                    elif c == [255, 0, 255]: desc = "Magenta"
                    elif c == [255, 255, 255]: desc = "White"
                    elif c == [255, 128, 0]: desc = "Orange"
                    
                    print(f"    {name:<15} {str(c):<20} {desc}")

        # Also save simple point cloud (one vertex per joint) for easy loading
        points_path = filepath.replace('.ply', '_points.ply')
        points = []
        for name in joint_order:
            if name in joints:
                points.append(joints[name])
            else:
                # Use NaN for missing joints (will be filtered on load)
                points.append(np.array([np.nan, np.nan, np.nan]))

        if points:
            point_cloud = trimesh.PointCloud(vertices=np.array(points))
            point_cloud.export(points_path)

    def _get_anny_joint_positions(
        self,
        phenotypes: dict[str, float],
    ) -> dict[str, np.ndarray]:
        """
        Get ANNY joint positions for given phenotypes.

        Args:
            phenotypes: Phenotype parameters

        Returns:
            Dictionary of joint names to 3D positions
        """
        coeffs = self._model.get_phenotype_blendshape_coefficients(**phenotypes)

        # Get bone head positions
        template_heads = self._model.template_bone_heads.detach().cpu().numpy()
        blendshapes = self._model.bone_heads_blendshapes.detach().cpu().numpy()
        coeffs_np = coeffs[0].detach().cpu().numpy()

        # Blend: template + sum(coeff_i * blendshape_i)
        blended_heads = template_heads + np.einsum("i,ijk->jk", coeffs_np, blendshapes)

        # Map ANNY bone names to our joint names
        bone_labels = self._model.bone_labels
        joint_mapping = {
            "pelvis": "root",
            "hip_l": "pelvis.L",      # Anatomically closer to the hip joint origin
            "hip_r": "pelvis.R",
            "knee_l": "lowerleg01.L",
            "knee_r": "lowerleg01.R",
            "ankle_l": "foot.L",
            "ankle_r": "foot.R",
            "shoulder_l": "shoulder01.L", # Shoulder pivot
            "shoulder_r": "shoulder01.R",
            "elbow_l": "lowerarm01.L",
            "elbow_r": "lowerarm01.R",
            "wrist_l": "wrist.L",
            "wrist_r": "wrist.R",
            "neck": "neck01",
            "head": "head",
            # Additional MHR70 joints
            "olecranon_l": "lowerarm01.L", # Elbow back
            "olecranon_r": "lowerarm01.R",
            "acromion_l": "shoulder01.L",  # Shoulder top
            "acromion_r": "shoulder01.R",
        }

        joints = {}
        for our_name, anny_name in joint_mapping.items():
            if anny_name in bone_labels:
                idx = bone_labels.index(anny_name)
                joints[our_name] = blended_heads[idx]

        return joints

    def _compute_pose_from_joints(
        self,
        source_joints: dict[str, np.ndarray],
        target_joints: dict[str, np.ndarray],
        rest_bone_poses: np.ndarray | None = None,
        bone_labels: list[str] | None = None,
    ) -> dict[str, np.ndarray]:
        """
        Compute bone rotations to move source joints to target joint positions.
        Delegates to ANNYPoseSolver for hierarchical solving.
        """
        if bone_labels is None:
            bone_labels = self._model.bone_labels
            
        solver = ANNYPoseSolver(bone_labels)
        return solver.compute_pose(source_joints, target_joints, rest_bone_poses)

    def _apply_pose_to_anny(
        self,
        phenotypes: dict[str, float],
        bone_rotations: dict[str, np.ndarray],
    ) -> np.ndarray:
        """
        Apply bone rotations to ANNY to generate a posed mesh.

        Args:
            phenotypes: Phenotype parameters for body shape
            bone_rotations: Dictionary of bone names to rotation vectors (axis-angle)

        Returns:
            Posed ANNY vertices as numpy array [V, 3]
        """
        from scipy.spatial.transform import Rotation

        # Get the list of bone labels from ANNY
        bone_labels = self._model.bone_labels
        num_bones = len(bone_labels)

        # Create pose parameter tensor as 4x4 homogeneous matrices (identity = no rotation)
        # ANNY expects BxJx4x4 format
        pose_params = torch.eye(4, device=self.device, dtype=self.dtype).unsqueeze(0).unsqueeze(0)
        pose_params = pose_params.repeat(1, num_bones, 1, 1)  # [1, num_bones, 4, 4]

        # Apply our computed rotations to the appropriate bones
        for bone_name, rotvec in bone_rotations.items():
            if bone_name in bone_labels:
                bone_idx = bone_labels.index(bone_name)
                # Convert axis-angle to rotation matrix
                if np.linalg.norm(rotvec) > 1e-6:
                    rot_mat = Rotation.from_rotvec(rotvec).as_matrix()
                    # Create 4x4 homogeneous matrix (rotation only, no translation)
                    homo_mat = np.eye(4)
                    homo_mat[:3, :3] = rot_mat
                    pose_params[0, bone_idx] = torch.tensor(
                        homo_mat, device=self.device, dtype=self.dtype
                    )

        # Get phenotype coefficients
        phenotype_kwargs = {k: torch.tensor([[v]], device=self.device, dtype=self.dtype)
                           for k, v in phenotypes.items()}

        # Get rest pose mesh to find pelvis position before posing
        rest_output = self._model(
            pose_parameters=None,  # No pose = rest pose
            phenotype_kwargs=phenotype_kwargs,
            pose_parameterization="rest_relative",
            return_bone_ends=True,
        )
        rest_verts = rest_output["vertices"][0].detach().cpu().numpy()

        # Find pelvis center in rest pose (use root bone head position)
        bone_labels = self._model.bone_labels
        if "root" in bone_labels and "bone_heads" in rest_output:
            root_idx = bone_labels.index("root")
            rest_bone_heads = rest_output["bone_heads"][0].detach().cpu().numpy()
            rest_pelvis_pos = rest_bone_heads[root_idx]
        else:
            # Fallback: use mesh centroid at pelvis height
            rest_pelvis_pos = rest_verts.mean(axis=0)

        # Generate posed mesh using rest_relative parameterization
        # (delta transforms are applied relative to rest pose)
        output = self._model(
            pose_parameters=pose_params,
            phenotype_kwargs=phenotype_kwargs,
            pose_parameterization="rest_relative",
            return_bone_ends=True,
        )

        posed_verts = output["vertices"][0].detach().cpu().numpy()

        # Find pelvis position after posing
        if "root" in bone_labels and "bone_heads" in output:
            posed_bone_heads = output["bone_heads"][0].detach().cpu().numpy()
            posed_pelvis_pos = posed_bone_heads[root_idx]
        else:
            posed_pelvis_pos = posed_verts.mean(axis=0)

        # Anchor pelvis: shift posed mesh so pelvis stays in same position
        pelvis_shift = rest_pelvis_pos - posed_pelvis_pos
        posed_verts = posed_verts + pelvis_shift

        return posed_verts

    def _estimate_initial_phenotypes(
        self,
        landmarks: dict,
        user_height_cm: float | None,
        user_gender: str | None,
    ) -> dict[str, float]:
        """
        Phase 2: Estimate initial phenotypes from mesh characteristics.

        Uses mesh proportions and volume to estimate weight, muscle, etc.
        This gives ParametersRegressor a much better starting point than 0.5.

        Args:
            landmarks: Output from _extract_skeletal_landmarks
            user_height_cm: User's actual height
            user_gender: User's gender

        Returns:
            Dictionary of initial phenotype values (0-1 scale)
        """
        # ANNY only has these phenotypes: gender, age, muscle, weight, height, proportions
        phenotypes = {
            "gender": 1.0 if user_gender and user_gender.lower() == "female" else 0.0,
            "age": 0.4,  # Default to young adult
            "height": 0.5,
            "weight": 0.5,
            "muscle": 0.5,
            "proportions": 0.5,
        }

        # Estimate height phenotype
        if user_height_cm:
            # ANNY height phenotype 0.0 -> ~1.5m, 1.0 -> ~2.0m (roughly)
            # Map user height to phenotype
            height_m = user_height_cm / 100.0
            # Linear mapping: 1.5m -> 0.0, 2.0m -> 1.0
            height_pheno = (height_m - 1.5) / 0.5
            phenotypes["height"] = np.clip(height_pheno, 0.05, 0.95)

        # Estimate weight phenotype from circumferences
        circs = landmarks.get("circumferences", {})
        if "hips" in circs and "waist" in circs:
            # Average circumference gives rough body volume indicator
            avg_circ = (circs.get("bust", 0) + circs.get("waist", 0) + circs.get("hips", 0)) / 3
            mesh_height = landmarks.get("height", 1.7)

            # Normalize by height to get "thickness" ratio
            # Thicker person -> higher weight phenotype
            if user_height_cm:
                # Scale circumference to real-world size
                scale = (user_height_cm / 100.0) / mesh_height
                avg_circ_real = avg_circ * scale * 100  # in cm

                # Map circumference to weight phenotype
                # Rough mapping: 70cm avg -> 0.3, 90cm avg -> 0.5, 110cm avg -> 0.7
                weight_pheno = (avg_circ_real - 70) / 60 + 0.3
                phenotypes["weight"] = np.clip(weight_pheno, 0.1, 0.95)

        # Estimate body proportions from waist/hip ratio
        if "waist" in circs and "hips" in circs and circs["hips"] > 0:
            wh_ratio = circs["waist"] / circs["hips"]
            # Lower W/H ratio -> more curvy -> adjust proportions
            if wh_ratio < 0.75:
                phenotypes["proportions"] = 0.6
            elif wh_ratio > 0.85:
                phenotypes["proportions"] = 0.4

        return phenotypes

    def _icp_align(
        self,
        source: np.ndarray,
        target: np.ndarray,
        max_iterations: int = 50,
        rotation_scale: float = 0.3,
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Align source points to target using ICP (Iterative Closest Point).

        Args:
            source: Nx3 source points (will be transformed)
            target: Mx3 target points (reference)
            max_iterations: Maximum ICP iterations
            rotation_scale: Scale factor for rotation (0=translation only, 1=full rotation)

        Returns:
            Tuple of (aligned_source, rotation_matrix, translation)
        """
        from scipy.spatial import cKDTree
        from scipy.spatial.transform import Rotation

        source_centered = source - source.mean(axis=0)
        target_centered = target - target.mean(axis=0)

        # Build KD-tree for target
        tree = cKDTree(target_centered)

        current = source_centered.copy()
        R_total = np.eye(3)
        t_total = np.zeros(3)

        for _ in range(max_iterations):
            # Find closest points
            distances, indices = tree.query(current, k=1)

            # Get corresponding target points
            target_pts = target_centered[indices]

            # Compute optimal rotation using SVD
            H = current.T @ target_pts
            U, S, Vt = np.linalg.svd(H)
            R = Vt.T @ U.T

            # Handle reflection case
            if np.linalg.det(R) < 0:
                Vt[-1, :] *= -1
                R = Vt.T @ U.T

            # Scale down the rotation to prevent over-rotation
            if rotation_scale < 1.0:
                rotvec = Rotation.from_matrix(R).as_rotvec()
                R = Rotation.from_rotvec(rotvec * rotation_scale).as_matrix()

            # Apply rotation
            current = current @ R.T
            R_total = R @ R_total

            # Check convergence
            if np.mean(distances) < 0.001:
                break

        return current + target.mean(axis=0), R_total, t_total

    def _create_anny_topology_target(
        self,
        sam3d_mesh: trimesh.Trimesh,
        initial_phenotypes: dict[str, float],
        bone_rotations: dict[str, np.ndarray] | None = None,
        save_debug_prefix: str | None = None,
    ) -> torch.Tensor:
        """
        Phase 3: Create ANNY-topology target using posed ANNY + closest-point.

        1. Generate ANNY mesh with estimated phenotypes
        2. Apply bone rotations to match SAM-3D pose (if provided)
        3. Scale ANNY to match SAM-3D height
        4. ICP align ANNY to SAM-3D (rigid rotation for fine alignment)
        5. Find closest points on SAM-3D for each ANNY vertex

        Args:
            sam3d_mesh: SAM-3D mesh (already scaled to user's height)
            initial_phenotypes: Estimated phenotypes from Phase 2
            bone_rotations: Optional bone rotations to pose ANNY like SAM-3D
            save_debug_prefix: Optional path prefix for debug meshes

        Returns:
            Tensor of shape [1, V, 3] with ANNY topology matching SAM-3D shape
        """
        # Get ANNY mesh - either posed or T-pose
        if bone_rotations:
            # Apply pose to match SAM-3D
            anny_template = self._apply_pose_to_anny(initial_phenotypes, bone_rotations)
            if save_debug_prefix:
                print(f"  Phase 3 - Using POSED ANNY with {len(bone_rotations)} bone rotations")
        else:
            # Fall back to T-pose
            coeffs = self._model.get_phenotype_blendshape_coefficients(**initial_phenotypes)
            anny_template = self._model.get_rest_vertices(coeffs)[0].detach().cpu().numpy()
            if save_debug_prefix:
                print(f"  Phase 3 - Using T-pose ANNY (no bone rotations)")

        # Scale ANNY template to match SAM-3D mesh height
        anny_height = anny_template[:, 2].max() - anny_template[:, 2].min()
        sam3d_height = sam3d_mesh.vertices[:, 2].max() - sam3d_mesh.vertices[:, 2].min()
        scale = sam3d_height / anny_height
        anny_template_scaled = anny_template * scale

        # Center both meshes
        anny_centered = anny_template_scaled - anny_template_scaled.mean(axis=0)
        sam3d_centered = sam3d_mesh.vertices - sam3d_mesh.vertices.mean(axis=0)

        # ICP align ANNY to SAM-3D (rigid rotation for fine alignment)
        anny_aligned, R, t = self._icp_align(anny_centered, sam3d_centered)

        # Apply empirically-determined corrections (from manual Blender alignment)
        # 1. Rotate -3 degrees around X-axis (ANNY tilts back to match SAM-3D)
        angle_x = np.radians(-3.0)
        Rx = np.array([
            [1, 0, 0],
            [0, np.cos(angle_x), -np.sin(angle_x)],
            [0, np.sin(angle_x), np.cos(angle_x)]
        ])
        anny_aligned = anny_aligned @ Rx.T

        # 2. Rotate -5 degrees around Z-axis (test for bust improvement)
        angle_z = np.radians(-5.0)
        Rz = np.array([
            [np.cos(angle_z), -np.sin(angle_z), 0],
            [np.sin(angle_z), np.cos(angle_z), 0],
            [0, 0, 1]
        ])
        anny_aligned = anny_aligned @ Rz.T

        # 3. Translation offset
        alignment_offset = np.array([0.01, -0.03, 0.03])  # meters
        anny_aligned = anny_aligned + alignment_offset

        # Save debug mesh: ANNY after posing and ICP alignment
        # if save_debug_prefix:
        #     anny_faces = self._model.get_triangular_faces().cpu().numpy()
        #     aligned_mesh = trimesh.Trimesh(
        #         vertices=anny_aligned, faces=anny_faces, process=False
        #     )
        #     aligned_mesh.export(f"{save_debug_prefix}_anny_posed_aligned.ply")

        # Create SAM-3D mesh for surface queries
        sam3d_mesh_centered = trimesh.Trimesh(
            vertices=sam3d_centered, faces=sam3d_mesh.faces, process=False
        )

        # For each ANNY vertex, find closest point on SAM-3D surface
        closest_points, distances, triangle_ids = sam3d_mesh_centered.nearest.on_surface(
            anny_aligned
        )

        # Save debug mesh: the target we're fitting to
        # if save_debug_prefix:
        #     target_mesh = trimesh.Trimesh(
        #         vertices=closest_points, faces=anny_faces, process=False
        #     )
        #     target_mesh.export(f"{save_debug_prefix}_target_vertices.ply")
        #     print(f"  Phase 3 - ICP mean distance: {np.mean(distances):.4f}m")

        return torch.from_numpy(closest_points.astype(np.float32)).to(
            device=self.device, dtype=self.dtype
        )[None]  # [1, V, 3]

    async def analyze_from_url(
        self,
        ply_url: str,
        user_height_cm: float | None = None,
        keypoints_3d: list[list[float]] | None = None,
    ) -> FittingResult:
        """
        Analyze body from SAM-3D-Body PLY mesh URL.

        Args:
            ply_url: URL to the PLY mesh file from SAM-3D-Body
            user_height_cm: Optional user-provided height for calibration
            keypoints_3d: Optional 3D keypoints from SAM-3D-Body

        Returns:
            FittingResult with measurements and fitted parameters
        """
        # Download PLY file
        async with httpx.AsyncClient() as client:
            response = await client.get(ply_url)
            response.raise_for_status()
            ply_data = response.content

        # Load mesh with trimesh
        mesh = trimesh.load(io.BytesIO(ply_data), file_type="ply")
        vertices = np.array(mesh.vertices, dtype=np.float32)

        return self.analyze_from_vertices(
            vertices,
            user_height_cm=user_height_cm,
            keypoints_3d=keypoints_3d
        )

    def analyze_from_vertices(
        self,
        vertices: np.ndarray,
        user_height_cm: float | None = None,
        user_gender: str | None = None,
        user_weight_kg: float | None = None,
        keypoints_3d: list[list[float]] | None = None,
        faces: np.ndarray | None = None,
        save_debug_meshes: str | None = None,
    ) -> FittingResult:
        """
        Analyze body from mesh vertices using hierarchical fitting.

        Hierarchical approach:
        1. Phase 1: Extract skeletal landmarks from SAM-3D
        2. Phase 2: Estimate initial phenotypes from mesh characteristics
        3. Phase 3: Create ANNY-topology target with matched template
        4. Phase 4: Run ParametersRegressor for fine-tuning

        Args:
            vertices: Nx3 array of mesh vertex positions (Y-up from SAM-3D)
            user_height_cm: Required user-provided height for calibration
            user_gender: Optional gender ('male' or 'female') to constrain fitting
            user_weight_kg: Optional weight in kg to constrain fitting
            keypoints_3d: Optional 70x3 array of keypoints from SAM-3D
            faces: Optional Mx3 array of face indices for the mesh
            save_debug_meshes: Optional path prefix to save debug meshes

        Returns:
            FittingResult with measurements and confidence
        """
        self._ensure_regressor_loaded()

        # Detect and normalize mesh orientation
        z_range = vertices[:, 2].max() - vertices[:, 2].min()
        y_range = vertices[:, 1].max() - vertices[:, 1].min()

        if z_range > y_range:
            # Already Z-up (ANNY space)
            transformed = vertices.copy()
            print("  Input mesh detected as Z-up (ANNY space)")
        else:
            # RAW SAM-3D: X, Y(up), Z(depth) -> ANNY: X, -Z(forward), Y(up)
            transformed = vertices[:, [0, 2, 1]].copy()
            transformed[:, 1] *= -1  # Flip Y (was depth)
            print("  Input mesh detected as Y-up (Raw SAM-3D space)")

        # ===== CENTER AT PELVIS =====
        # Both mesh and keypoints should be pelvis-centered for alignment.
        # Find pelvis from mesh geometry (not keypoints - they're in a different coordinate space).

        # First, roughly center to make slicing work
        rough_center = transformed.mean(axis=0)
        transformed -= rough_center

        # Find pelvis level (~50-53% of height) using mesh slicing
        min_z = transformed[:, 2].min()
        max_z = transformed[:, 2].max()
        height = max_z - min_z
        pelvis_z = min_z + height * 0.52  # Pelvis is around 52% height

        # Create temp mesh for slicing
        if faces is not None:
            temp_mesh = trimesh.Trimesh(vertices=transformed, faces=faces, process=False)
        else:
            temp_mesh = trimesh.PointCloud(transformed).convex_hull

        # Find pelvis center from mesh slice
        pelvis_slice = temp_mesh.section(plane_normal=[0, 0, 1], plane_origin=[0, 0, pelvis_z])
        if pelvis_slice and pelvis_slice.discrete:
            # Find largest loop (torso, not legs)
            largest_loop = max(pelvis_slice.discrete, key=lambda l: len(l))
            pelvis_xy = largest_loop[:, :2].mean(axis=0)
            mesh_pelvis = np.array([pelvis_xy[0], pelvis_xy[1], pelvis_z])
        else:
            # Fallback: pelvis at origin (mesh already roughly centered)
            mesh_pelvis = np.array([0.0, 0.0, pelvis_z])

        # Re-center at pelvis
        transformed -= mesh_pelvis
        print(f"  Centered mesh at pelvis: [{mesh_pelvis[0]:.3f}, {mesh_pelvis[1]:.3f}, {mesh_pelvis[2]:.3f}]")

        # Create mesh for landmark extraction
        if faces is not None:
            sam3d_mesh = trimesh.Trimesh(vertices=transformed, faces=faces, process=False)
        else:
            sam3d_mesh = trimesh.Trimesh(vertices=transformed)
            sam3d_mesh = sam3d_mesh.convex_hull

        # ===== PHASE 1: Extract skeletal landmarks =====
        landmarks = self._extract_skeletal_landmarks(sam3d_mesh)

        # ===== PHASE 1b: Extract joint positions =====
        # Keypoints from _extract_joints_from_keypoints are already pelvis-centered,
        # so they will align with the pelvis-centered mesh.
        sam3d_keypoints_all = None
        if keypoints_3d:
            sam3d_joints, sam3d_keypoints_all = self._extract_joints_from_keypoints(keypoints_3d)
            print(f"  Phase 1b - Loaded {len(sam3d_joints)} joints from SAM-3D keypoints (pelvis-centered)")
        else:
            sam3d_joints = self._extract_joint_positions(sam3d_mesh)
            print(f"  Phase 1b - Extracted {len(sam3d_joints)} joints from SAM-3D mesh slices")

        if save_debug_meshes:
            self._save_joints_debug(sam3d_joints, f"{save_debug_meshes}_sam3d_joints.ply")

        # ===== PHASE 2: Estimate initial phenotypes =====
        initial_phenotypes = self._estimate_initial_phenotypes(
            landmarks, user_height_cm, user_gender
        )

        if save_debug_meshes:
            print(f"  Phase 2 - Initial phenotypes: weight={initial_phenotypes['weight']:.2f}, "
                  f"height={initial_phenotypes['height']:.2f}, muscle={initial_phenotypes['muscle']:.2f}")

        # Scale SAM-3D mesh to user's height
        sam3d_height = landmarks["height"]
        if user_height_cm:
            target_height_m = user_height_cm / 100.0
            scale_to_real = target_height_m / sam3d_height
            scaled_verts = transformed * scale_to_real
            sam3d_mesh = trimesh.Trimesh(
                vertices=scaled_verts,
                faces=sam3d_mesh.faces,
                process=False,
            )
            # Scale raw keypoints too
            if sam3d_keypoints_all is not None:
                sam3d_keypoints_all *= scale_to_real

        # Save debug mesh: SAM-3D transformed
        if save_debug_meshes:
            sam3d_mesh.export(f"{save_debug_meshes}_sam3d_scaled.ply")
            if sam3d_keypoints_all is not None:
                self._save_all_keypoints_debug(sam3d_keypoints_all, f"{save_debug_meshes}_sam3d_keypoints_all.ply")
                print(f"  Saved all {len(sam3d_keypoints_all)} keypoints to {save_debug_meshes}_sam3d_keypoints_all.ply")

        # ===== PHASE 2b: Get ANNY joint positions and compute pose =====
        # Get ANNY T-pose joint positions
        anny_joints = self._get_anny_joint_positions(initial_phenotypes)

        # 1. Normalize both joint sets by centering at pelvis
        # This makes them global-translation invariant
        if "pelvis" in anny_joints:
            anny_pelvis = anny_joints["pelvis"]
            anny_joints_centered = {k: v - anny_pelvis for k, v in anny_joints.items()}
        else:
            anny_joints_centered = anny_joints

        if "pelvis" in sam3d_joints:
            sam3d_pelvis = sam3d_joints["pelvis"]
            # SAM-3D keypoints are already flipped/transformed by _extract_joints_from_keypoints
            sam3d_joints_centered = {k: v - sam3d_pelvis for k, v in sam3d_joints.items()}
        else:
            sam3d_joints_centered = sam3d_joints

        # 2. Scale both to real-world meters (T-pose height)
        if user_height_cm:
            # ANNY scale
            coeffs_temp = self._model.get_phenotype_blendshape_coefficients(**initial_phenotypes)
            anny_verts_temp = self._model.get_rest_vertices(coeffs_temp)[0].detach().cpu().numpy()
            anny_mesh_height = anny_verts_temp[:, 2].max() - anny_verts_temp[:, 2].min()
            anny_scale = (user_height_cm / 100.0) / anny_mesh_height
            anny_joints_scaled = {k: v * anny_scale for k, v in anny_joints_centered.items()}
            
            # SAM-3D scale
            sam3d_scale = (user_height_cm / 100.0) / sam3d_height
            sam3d_joints_scaled = {k: v * sam3d_scale for k, v in sam3d_joints_centered.items()}
        else:
            anny_joints_scaled = anny_joints_centered
            sam3d_joints_scaled = sam3d_joints_centered

        if save_debug_meshes:
            # self._save_joints_debug(anny_joints_scaled, f"{save_debug_meshes}_anny_joints.ply")
            # self._save_joints_debug(sam3d_joints_scaled, f"{save_debug_meshes}_sam3d_joints.ply")
            print(f"  Phase 2b - ANNY has {len(anny_joints)} joints, SAM-3D has {len(sam3d_joints)} joints")

            # Debug: Compare key joint positions (already pelvis-aligned)
            print(f"\n  === JOINT POSITION COMPARISON (Pelvis-centered) ===")
            for joint_name in ["shoulder_l", "shoulder_r", "hip_l", "hip_r"]:
                if joint_name in anny_joints_scaled and joint_name in sam3d_joints_scaled:
                    anny_pos = anny_joints_scaled[joint_name]
                    sam3d_pos = sam3d_joints_scaled[joint_name]
                    diff = sam3d_pos - anny_pos
                    print(f"  {joint_name}:")
                    print(f"    ANNY:  [{anny_pos[0]:+.3f}, {anny_pos[1]:+.3f}, {anny_pos[2]:+.3f}]")
                    print(f"    SAM3D: [{sam3d_pos[0]:+.3f}, {sam3d_pos[1]:+.3f}, {sam3d_pos[2]:+.3f}]")
                    print(f"    DIFF:  [{diff[0]:+.3f}, {diff[1]:+.3f}, {diff[2]:+.3f}]")

        # Get rest bone poses for world→local rotation transformation
        # This returns (bone_heads, bone_tails, rest_bone_poses) where rest_bone_poses is [J, 4, 4]
        _, _, rest_bone_poses = self._model.get_rest_bone_poses(coeffs_temp)
        rest_bone_poses_np = rest_bone_poses[0].detach().cpu().numpy()  # Remove batch dim

        # Compute bone rotations to match SAM-3D pose (now with proper local-space transform)
        bone_rotations = self._compute_pose_from_joints(
            anny_joints_scaled,
            sam3d_joints_scaled,
            rest_bone_poses=rest_bone_poses_np,
            bone_labels=self._model.bone_labels,
        )
        if save_debug_meshes:
            print(f"  Phase 2b - Computed {len(bone_rotations)} bone rotations (local space)")

        # ===== PHASE 3: Create ANNY-topology target =====
        # Use posed ANNY for closest-point matching (not T-pose)
        target_vertices = self._create_anny_topology_target(
            sam3d_mesh,
            initial_phenotypes,
            bone_rotations=bone_rotations,
            save_debug_prefix=save_debug_meshes
        )

        # Set up excluded phenotypes (freeze known values)
        # Height and gender are provided by user - don't optimize them!
        # Muscle tends to go to extremes - freeze it at 0.5
        excluded_phenotypes = ["height", "muscle"]
        if user_gender:
            excluded_phenotypes.append("gender")

        # ===== PHASE 4: Run ParametersRegressor =====
        pose_params, phenotype_kwargs, fitted_verts = self._regressor(
            vertices_target=target_vertices,
            initial_phenotype_kwargs=initial_phenotypes,
            optimize_phenotypes=True,
            excluded_phenotypes=excluded_phenotypes,
        )

        # Extract phenotype values
        best_params = {k: float(v[0]) for k, v in phenotype_kwargs.items()}

        if save_debug_meshes:
            print(f"  Phase 4 - Final phenotypes: weight={best_params['weight']:.2f}, "
                  f"height={best_params['height']:.2f}, muscle={best_params['muscle']:.2f}")

            from scipy.spatial.transform import Rotation as R

            bone_labels_debug = self._model.bone_labels
            num_bones_debug = len(bone_labels_debug)
            anny_faces = self._model.get_triangular_faces().cpu().numpy()

            # ===== STEP 1: Build pose parameters =====
            # Start with identity (T-pose)
            pose_params = torch.eye(4, device=self.device, dtype=self.dtype).unsqueeze(0).unsqueeze(0)
            pose_params = pose_params.repeat(1, num_bones_debug, 1, 1)

            # Apply root rotation first
            if "root" in bone_rotations and "root" in bone_labels_debug:
                root_rotvec = bone_rotations["root"]
                if np.linalg.norm(root_rotvec) > 1e-6:
                    root_idx = bone_labels_debug.index("root")
                    rot_mat = R.from_rotvec(root_rotvec).as_matrix()
                    homo_mat = np.eye(4)
                    homo_mat[:3, :3] = rot_mat
                    pose_params[0, root_idx] = torch.tensor(homo_mat, device=self.device, dtype=self.dtype)
                    print(f"  Applied root rotation: {np.degrees(root_rotvec)} deg")

            # ===== STEP 2: Generate REST mesh (root rotation only) =====
            rest_output = self._model(
                pose_parameters=pose_params,
                phenotype_kwargs=phenotype_kwargs,
                pose_parameterization="rest_relative",
                return_bone_ends=True,
            )
            rest_verts = rest_output["vertices"][0].detach().cpu().numpy()
            rest_bone_heads = rest_output["bone_heads"][0].detach().cpu().numpy()

            # Get pelvis position for centering (will use for both meshes)
            root_idx = bone_labels_debug.index("root")
            pelvis_pos = rest_bone_heads[root_idx].copy()
            pelvis_pos[1] -= 0.08  # Y offset to align with SAM-3D

            # Center and scale
            rest_verts -= pelvis_pos
            rest_height = rest_verts[:, 2].max() - rest_verts[:, 2].min()
            pose_scale = (user_height_cm / 100.0) / rest_height if user_height_cm else 1.0
            rest_verts_scaled = rest_verts * pose_scale

            # Save REST mesh
            rest_mesh = trimesh.Trimesh(vertices=rest_verts_scaled, faces=anny_faces, process=False)
            rest_mesh.export(f"{save_debug_meshes}_anny_rest.ply")
            print(f"  Saved debug_anny_rest.ply (root rotation only)")

            # ===== STEP 3: Add bone rotations for POSED mesh =====
            print(f"  Adding bone rotations:")
            for bone_name, rotvec in bone_rotations.items():
                if bone_name == "root":
                    continue  # Already applied
                if bone_name in bone_labels_debug and np.linalg.norm(rotvec) > 1e-6:
                    bone_idx = bone_labels_debug.index(bone_name)
                    rot_mat = R.from_rotvec(rotvec).as_matrix()
                    homo_mat = np.eye(4)
                    homo_mat[:3, :3] = rot_mat
                    pose_params[0, bone_idx] = torch.tensor(homo_mat, device=self.device, dtype=self.dtype)
                    print(f"    {bone_name}: {np.degrees(rotvec)} deg")

            # ===== STEP 4: Generate POSED mesh (root + bone rotations) =====
            posed_output = self._model(
                pose_parameters=pose_params,
                phenotype_kwargs=phenotype_kwargs,
                pose_parameterization="rest_relative",
                return_bone_ends=True,
            )
            posed_verts = posed_output["vertices"][0].detach().cpu().numpy()

            # Use SAME centering as rest mesh
            posed_verts -= pelvis_pos
            posed_verts_scaled = posed_verts * pose_scale

            # Save POSED mesh
            posed_mesh = trimesh.Trimesh(vertices=posed_verts_scaled, faces=anny_faces, process=False)
            posed_mesh.export(f"{save_debug_meshes}_anny_posed.ply")
            print(f"  Saved debug_anny_posed.ply (root + bone rotations)")

            # Save POSED joint positions for comparison with SAM-3D joints
            if "bone_heads" in posed_output:
                posed_bone_heads = posed_output["bone_heads"][0].detach().cpu().numpy()
                # Apply same centering as mesh (pelvis offset)
                posed_bone_heads_centered = posed_bone_heads - pelvis_pos
                # Scale to match user height
                posed_bone_heads_scaled = posed_bone_heads_centered * pose_scale
                # Convert to joint dict using bone labels
                posed_joints = {}
                bone_labels = self._model.bone_labels
                # Map bone names to our joint names
                bone_to_joint = {
                    "upperarm01.L": "shoulder_l",
                    "upperarm01.R": "shoulder_r",
                    "lowerarm01.L": "elbow_l",
                    "lowerarm01.R": "elbow_r",
                    "wrist.L": "wrist_l",
                    "wrist.R": "wrist_r",
                    "upperleg01.L": "hip_l",
                    "upperleg01.R": "hip_r",
                    "lowerleg01.L": "knee_l",
                    "lowerleg01.R": "knee_r",
                    "foot.L": "ankle_l",
                    "foot.R": "ankle_r",
                    "root": "pelvis",
                    "neck01": "neck",
                    "head": "head",
                }
                for i, bone_name in enumerate(bone_labels):
                    if bone_name in bone_to_joint:
                        posed_joints[bone_to_joint[bone_name]] = posed_bone_heads_scaled[i]
                self._save_joints_debug(posed_joints, f"{save_debug_meshes}_anny_posed_joints.ply")
                print(f"  Saved debug_anny_posed_joints.ply")

                # Debug: Compare posed joints to SAM-3D target
                # NOTE: SAM-3D uses opposite X convention (left = -X), so we flip X for comparison
                print(f"\n  === POSED vs TARGET JOINT COMPARISON (X-flipped for coordinate alignment) ===")
                for joint_name in ["shoulder_l", "shoulder_r", "hip_l", "hip_r"]:
                    if joint_name in posed_joints and joint_name in sam3d_joints_scaled:
                        posed_pos = posed_joints[joint_name]
                        # Flip X and apply pelvis offset to align coordinate systems
                        target_pos_aligned = np.array([
                            -sam3d_joints_scaled[joint_name][0],  # Flip X
                            sam3d_joints_scaled[joint_name][1],
                            sam3d_joints_scaled[joint_name][2]
                        ])
                        diff = posed_pos - target_pos_aligned
                        dist = np.linalg.norm(diff)
                        print(f"  {joint_name}:")
                        print(f"    POSED:  [{posed_pos[0]:+.3f}, {posed_pos[1]:+.3f}, {posed_pos[2]:+.3f}]")
                        print(f"    TARGET: [{target_pos_aligned[0]:+.3f}, {target_pos_aligned[1]:+.3f}, {target_pos_aligned[2]:+.3f}]")
                        print(f"    DIFF:   [{diff[0]:+.3f}, {diff[1]:+.3f}, {diff[2]:+.3f}] (dist: {dist:.3f}m)")

        # ===== PHASE 5: Measure in T-pose (rest pose) =====
        # Get measurements from fitted ANNY mesh in canonical pose
        coeffs = self._model.get_phenotype_blendshape_coefficients(**best_params)
        rest_vertices = self._model.get_rest_vertices(coeffs)

        # Get measurements from ANNY's Anthropometry
        anthro_measurements = self._anthropometry(rest_vertices)

        # Get full ANNY mesh for circumference measurements
        anny_verts = rest_vertices[0].detach().cpu().numpy()
        anny_faces = self._model.get_triangular_faces().cpu().numpy()
        anny_mesh = trimesh.Trimesh(vertices=anny_verts, faces=anny_faces, process=False)

        # ANNY mesh height
        anny_height = anny_verts[:, 2].max() - anny_verts[:, 2].min()

        # Get measurement heights from bone positions
        bust_z, hip_z = self._get_measurement_heights_from_bones(coeffs)

        bust_circ = self._measure_circumference(anny_mesh, bust_z)
        hip_circ = self._measure_circumference(anny_mesh, hip_z)
        waist_circ = float(anthro_measurements["waist_circumference"][0])

        # Apply calibration if user provided height
        if user_height_cm:
            scale = user_height_cm / (anny_height * 100)
        else:
            scale = 1.0

        # Convert to cm and apply scale
        height_cm = anny_height * 100 * scale
        bust_cm = bust_circ * 100 * scale
        waist_cm = waist_circ * 100 * scale
        hips_cm = hip_circ * 100 * scale
        mass_kg = float(anthro_measurements["mass"][0]) * (scale**3)
        bmi = float(anthro_measurements["bmi"][0])

        # Calculate confidence from per-vertex error (PVE)
        pve = torch.norm(
            fitted_verts - target_vertices[:, self._regressor.unique_ids], dim=-1
        ).mean()
        pve_mm = float(pve) * 1000  # Convert to mm
        confidence = max(0.0, min(1.0, 1.0 - pve_mm / 50.0))

        # Scale ANNY mesh to match user height for comparison
        anny_verts_scaled = anny_verts * scale

        # Save debug mesh: ANNY fitted (scaled to user height)
        if save_debug_meshes:
            anny_scaled_mesh = trimesh.Trimesh(
                vertices=anny_verts_scaled, faces=anny_faces, process=False
            )
            anny_scaled_mesh.export(f"{save_debug_meshes}_anny_fitted.ply")

        measurements = BodyMeasurements(
            height_cm=height_cm,
            bust_cm=bust_cm,
            waist_cm=waist_cm,
            hips_cm=hips_cm,
            weight_kg=mass_kg,
            bmi=bmi,
            gender_param=best_params.get("gender", 0.5),
            age_param=best_params.get("age", 0.5),
            muscle_param=best_params.get("muscle", 0.5),
            weight_param=best_params.get("weight", 0.5),
        )

        return FittingResult(
            measurements=measurements,
            phenotypes=best_params,
            fitted_vertices=anny_verts_scaled,
            confidence=confidence,
        )

    def _fit_phenotypes(
        self,
        target_vertices: np.ndarray,
        known_gender: str | None = None,
        known_weight_kg: float | None = None,
        faces: np.ndarray | None = None,
    ) -> tuple[dict, float]:
        """
        Fit ANNY phenotype parameters to match target mesh.

        Uses pose-invariant descriptors (circumferences at anatomical landmarks)
        instead of chamfer distance, which is sensitive to pose differences.

        Args:
            target_vertices: Centered target mesh vertices (Z-up)
            known_gender: If provided, use this instead of fitting ('male'/'female')
            known_weight_kg: If provided, use to estimate weight phenotype
            faces: Optional face indices for the mesh
        """
        target_height = target_vertices[:, 2].max() - target_vertices[:, 2].min()
        target_min_z = target_vertices[:, 2].min()

        # Create target mesh for circumference measurement
        if faces is not None:
            target_mesh = trimesh.Trimesh(vertices=target_vertices, faces=faces, process=False)
        else:
            # Fallback to convex hull if no faces provided
            target_mesh = trimesh.Trimesh(vertices=target_vertices)
            target_mesh = target_mesh.convex_hull

        # Find anatomical positions dynamically by scanning the mesh
        bust_z, waist_z, hip_z = self._find_measurement_positions(target_mesh, target_min_z, target_height)

        # Measure target circumferences - use RATIOS not absolute values
        # since SAM-3D has no scale reference
        target_bust = self._measure_circumference(target_mesh, bust_z)
        target_waist = self._measure_circumference(target_mesh, waist_z)
        target_hips = self._measure_circumference(target_mesh, hip_z)
        target_waist_hip_ratio = target_waist / target_hips if target_hips > 0 else 0.8
        target_bust_hip_ratio = target_bust / target_hips if target_hips > 0 else 1.0

        # Determine gender parameter
        if known_gender:
            gender_values = [0.0] if known_gender.lower() == "male" else [1.0]
        else:
            gender_values = [0.0, 1.0]  # Try both

        # Estimate weight phenotype from known weight if available
        # ANNY weight 0.0-1.0 roughly maps to BMI range
        if known_weight_kg and target_height > 0:
            # Rough estimate: weight phenotype correlates with BMI
            height_m = target_height  # Already in meters (ANNY scale)
            bmi_estimate = known_weight_kg / (height_m * height_m * 10000)  # Adjust for scale
            # Map BMI ~18-40 to weight 0.2-1.0
            weight_estimate = np.clip((bmi_estimate - 18) / 22 * 0.8 + 0.2, 0.2, 1.0)
            weight_values = [weight_estimate - 0.1, weight_estimate, weight_estimate + 0.1]
            weight_values = [np.clip(w, 0.1, 1.0) for w in weight_values]
        else:
            # Full range to capture thin to heavy bodies
            weight_values = [0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]

        # First, find best height phenotype
        best_height = 0.5
        best_height_diff = float("inf")
        for h in np.linspace(0.0, 1.0, 21):
            coeffs = self._model.get_phenotype_blendshape_coefficients(
                gender=0.5, age=0.5, muscle=0.5, weight=0.5, height=float(h)
            )
            verts = self._model.get_rest_vertices(coeffs)[0].detach().cpu().numpy()
            anny_h = verts[:, 2].max() - verts[:, 2].min()
            diff = abs(anny_h - target_height)
            if diff < best_height_diff:
                best_height_diff = diff
                best_height = float(h)

        # Grid search using pose-invariant circumference comparison
        best_score = float("inf")
        best_params = {
            "height": best_height,
            "weight": 0.5,
            "muscle": 0.5,
            "gender": gender_values[0],
            "age": 0.4,
        }

        for weight in weight_values:
            for muscle in [0.2, 0.4, 0.6, 0.8]:
                for gender in gender_values:
                    coeffs = self._model.get_phenotype_blendshape_coefficients(
                        gender=gender,
                        age=0.4,
                        muscle=muscle,
                        weight=float(weight),
                        height=best_height,
                    )

                    # Get ANNY circumferences at bone positions
                    bust_z, hip_z = self._get_measurement_heights_from_bones(coeffs)
                    verts = self._model.get_rest_vertices(coeffs)[0].detach().cpu().numpy()
                    faces = self._model.get_triangular_faces().cpu().numpy()
                    anny_mesh = trimesh.Trimesh(vertices=verts, faces=faces, process=False)

                    anny_bust = self._measure_circumference(anny_mesh, bust_z)
                    anny_waist = float(self._anthropometry(
                        self._model.get_rest_vertices(coeffs)
                    )["waist_circumference"][0])
                    anny_hips = self._measure_circumference(anny_mesh, hip_z)

                    anny_waist_hip_ratio = anny_waist / anny_hips if anny_hips > 0 else 0.8
                    anny_bust_hip_ratio = anny_bust / anny_hips if anny_hips > 0 else 1.0

                    # Score = ratio differences (scale-invariant since SAM-3D has no absolute scale)
                    score = (
                        (anny_waist_hip_ratio - target_waist_hip_ratio) ** 2
                        + (anny_bust_hip_ratio - target_bust_hip_ratio) ** 2
                    )

                    if score < best_score:
                        best_score = score
                        best_params = {
                            "height": best_height,
                            "weight": float(weight),
                            "muscle": muscle,
                            "gender": gender,
                            "age": 0.4,
                        }

        return best_params, best_score

    def _find_measurement_positions(
        self, mesh: trimesh.Trimesh, min_z: float, height: float
    ) -> tuple[float, float, float]:
        """
        Find anatomical measurement positions by scanning the mesh.

        - Bust: where arms split off (transition from 1 to 3 loops)
        - Waist: narrowest torso point between bust and hips
        - Hips: widest point in stable 3-loop region (torso + 2 legs)

        Returns:
            Tuple of (bust_z, waist_z, hip_z)
        """

        def get_loop_info(z: float) -> tuple[int, float, float]:
            """Get loop count, largest loop perimeter, and central loop perimeter."""
            path = mesh.section(plane_normal=[0, 0, 1], plane_origin=[0, 0, z])
            if path is None or not path.discrete:
                return 0, 0.0, 0.0

            loops = path.discrete
            num_loops = len(loops)

            largest_perim = 0.0
            central_perim = 0.0
            best_dist = float("inf")

            for loop in loops:
                loop_2d = loop[:, :2]
                if len(loop_2d) < 3:
                    continue
                cx, cy = loop_2d[:, 0].mean(), loop_2d[:, 1].mean()
                dist = np.sqrt(cx**2 + cy**2)
                perim = sum(
                    np.linalg.norm(loop_2d[i] - loop_2d[(i + 1) % len(loop_2d)])
                    for i in range(len(loop_2d))
                )
                # Track largest loop (torso should be biggest)
                if perim > largest_perim:
                    largest_perim = perim
                # Track most central loop
                if dist < best_dist:
                    best_dist = dist
                    central_perim = perim

            return num_loops, largest_perim, central_perim

        # Scan from top down to find bust (where arms split: 1 loop -> 3 loops)
        bust_z = min_z + height * 0.73  # Default fallback
        for pct in range(80, 65, -2):
            z = min_z + height * (pct / 100)
            num_loops, _, _ = get_loop_info(z)
            if num_loops >= 3:
                # Arms have split off - this is bust level
                bust_z = z
                break

        # Scan for hips: find widest point in STABLE 3-loop region
        # The torso loop should be the LARGEST loop (bigger than leg loops)
        # Scan from 52% to 62% to avoid unstable leg-merge regions at lower %
        hip_z = min_z + height * 0.55  # Default fallback
        max_hip_perim = 0.0
        for pct in range(52, 63):
            z = min_z + height * (pct / 100)
            num_loops, largest, central = get_loop_info(z)
            # Require exactly 3 loops (torso + 2 legs)
            # Use largest loop as body circumference (avoids leg merge artifacts)
            if num_loops == 3 and largest > max_hip_perim:
                max_hip_perim = largest
                hip_z = z

        # Waist is narrowest point between bust and hips
        waist_z = min_z + height * 0.62  # Default fallback
        min_waist_perim = float("inf")
        bust_pct = (bust_z - min_z) / height
        hip_pct = (hip_z - min_z) / height
        for pct_int in range(int(hip_pct * 100) + 2, int(bust_pct * 100) - 2):
            pct = pct_int / 100
            z = min_z + height * pct
            num_loops, largest, central = get_loop_info(z)
            # Use central loop for waist (torso, not arms)
            if num_loops >= 3 and central < min_waist_perim and central > 0:
                min_waist_perim = central
                waist_z = z

        return bust_z, waist_z, hip_z

    def _get_measurement_heights_from_bones(self, coeffs: torch.Tensor) -> tuple[float, float]:
        """
        Get Z-heights for bust and hip measurements from bone positions.

        Uses breast.L/R bones for bust and pelvis.L/R bones for hips.
        This is more accurate than fixed percentages which vary by body type.

        Args:
            coeffs: Phenotype blendshape coefficients

        Returns:
            Tuple of (bust_z, hip_z) heights for mesh slicing
        """
        # Get bone positions by applying phenotype blendshapes to template bones
        template_heads = self._model.template_bone_heads.detach().cpu().numpy()
        blendshapes = self._model.bone_heads_blendshapes.detach().cpu().numpy()
        coeffs_np = coeffs[0].detach().cpu().numpy()

        # Blend: template + sum(coeff_i * blendshape_i)
        blended_heads = template_heads + np.einsum("i,ijk->jk", coeffs_np, blendshapes)

        # Get bone indices
        bone_labels = self._model.bone_labels
        breast_l_idx = bone_labels.index("breast.L")
        breast_r_idx = bone_labels.index("breast.R")
        pelvis_l_idx = bone_labels.index("pelvis.L")
        pelvis_r_idx = bone_labels.index("pelvis.R")

        # Use average of left/right bone Z positions
        bust_z = (blended_heads[breast_l_idx, 2] + blended_heads[breast_r_idx, 2]) / 2
        hip_z = (blended_heads[pelvis_l_idx, 2] + blended_heads[pelvis_r_idx, 2]) / 2

        return float(bust_z), float(hip_z)

    def _measure_circumference(self, mesh: trimesh.Trimesh, z_level: float) -> float:
        """
        Measure circumference at a given Z level using mesh slicing.

        Finds the most central loop (closest to origin) to exclude arms.
        """
        path = mesh.section(plane_normal=[0, 0, 1], plane_origin=[0, 0, z_level])
        if path is None:
            return 0.0

        loops = path.discrete
        if not loops:
            return 0.0

        # Find the most central loop (torso) - excludes arms which are offset from center
        best_loop_perim = 0.0
        best_center_dist = float("inf")

        for loop in loops:
            loop_2d = loop[:, :2]  # Project to XY
            if len(loop_2d) < 3:
                continue

            # Calculate center of this loop
            center_x = loop_2d[:, 0].mean()
            center_y = loop_2d[:, 1].mean()
            center_dist = np.sqrt(center_x**2 + center_y**2)

            # Calculate perimeter
            perim = sum(
                np.linalg.norm(loop_2d[i] - loop_2d[(i + 1) % len(loop_2d)])
                for i in range(len(loop_2d))
            )

            # Pick the loop closest to center (torso, not arms)
            if center_dist < best_center_dist:
                best_center_dist = center_dist
                best_loop_perim = perim

        return best_loop_perim


# Convenience function for quick analysis
async def analyze_sam3d_output(
    ply_url: str,
    user_height_cm: float | None = None,
    device: str | None = None,
) -> FittingResult:
    """
    Analyze body measurements from SAM-3D-Body output.

    Args:
        ply_url: URL to PLY mesh from SAM-3D-Body
        user_height_cm: Optional user-provided height for calibration
        device: Torch device to use

    Returns:
        FittingResult with measurements and confidence
    """
    analyzer = ANNYBodyAnalyzer(device=device)
    return await analyzer.analyze_from_url(ply_url, user_height_cm)
