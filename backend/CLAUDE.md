# CLAUDE.md - Body Measurement Pipeline

## Overview

This backend extracts body measurements (bust, waist, hips) from 3D meshes produced by SAM-3D-Body, using NAVER's ANNY parametric body model.

## The Problem

**SAM-3D absolute measurements cannot be trusted.** The mesh has no real-world scale reference - it only captures the **relative shape/silhouette** of the person.

### What SAM-3D provides:
- Relative body proportions (waist/hip ratio, bust/hip ratio)
- Body silhouette shape
- Anatomical landmark positions (relative)

### What SAM-3D does NOT provide:
- Absolute measurements in cm/inches
- Actual height (mesh height varies by camera distance/angle)
- Actual weight

## Solution: Hierarchical SAM-3D → ANNY Fitting

### The Pipeline

```
User Input: Photo + Height + Gender
     ↓
SAM-3D-Body: Produces 3D mesh (no scale)
     ↓
Phase 1: Extract skeletal landmarks + joint positions from mesh
     ↓
Phase 2: Estimate initial ANNY phenotypes from mesh proportions
     ↓
Phase 2b: Compute bone rotations to match SAM-3D pose
     ↓
Phase 3: Pose ANNY → ICP align → Closest-point matching → ParametersRegressor
     ↓
Phase 4: Calibration regression (FUTURE - needs 550 person dataset)
     ↓
Phase 5: Measure in T-pose for clean results
     ↓
Output: Bust, Waist, Hips in cm + Body Type + Bridal Size
```

### Key Insight: Pose-Aware Vertex Matching

We now pose ANNY to match SAM-3D before doing closest-point vertex matching:

1. Extract joint positions from SAM-3D mesh (shoulders, elbows, wrists, hips, knees, ankles)
2. Compute bone rotations to align ANNY skeleton to SAM-3D pose
3. Generate posed ANNY mesh
4. ICP align posed ANNY to SAM-3D
5. Find closest points on SAM-3D for each ANNY vertex
6. Run ParametersRegressor for phenotype optimization
7. Measure in T-pose for clean, consistent results

## Current Implementation Status

### Completed (Phases 1-3)

**File:** `src/services/anny_integration.py`

1. **Phase 1: Skeletal Landmark Extraction** (`_extract_skeletal_landmarks`)
   - Finds bust level (where arms split from torso)
   - Finds waist level (narrowest torso point)
   - Finds hip level (widest point in pelvis region)
   - Extracts circumferences at each level

2. **Phase 1b: Joint Position Extraction** (`_extract_joint_positions`)
   - Extracts 15 joints from SAM-3D mesh by analyzing horizontal slices
   - Finds: pelvis, shoulders, elbows, wrists, hips, knees, ankles, neck, head
   - Uses loop analysis to detect where limbs split from torso

3. **Phase 2: Initial Phenotype Estimation** (`_estimate_initial_phenotypes`)
   - Maps user height to ANNY height phenotype
   - Estimates weight phenotype from circumference averages
   - Sets gender from user input

4. **Phase 2b: Pose Computation** (`_compute_pose_from_joints`, `_get_anny_joint_positions`)
   - Gets ANNY T-pose joint positions from bone heads
   - Computes bone rotations to align ANNY joints to SAM-3D joints
   - Outputs 4x4 homogeneous transformation matrices for 8 bones

5. **Phase 3: Posed Vertex Matching** (`_create_anny_topology_target`, `_apply_pose_to_anny`)
   - Applies bone rotations to pose ANNY like SAM-3D
   - ICP aligns posed ANNY to SAM-3D mesh
   - Finds closest points on SAM-3D surface for each ANNY vertex
   - Runs ParametersRegressor for phenotype optimization

### Current Accuracy (Single Sample)

With posed ANNY matching:
- **ICP mean distance:** 0.061m (38% better than T-pose matching at 0.099m)
- **Waist error:** -0.5 cm (was -3.3 cm with T-pose)
- **Hips error:** +4.7 cm
- **Bust error:** +8.3 cm
- **Weight error:** -2.9 kg (was -6.1 kg with T-pose)

### Known Limitations

1. **ANNY's expressible shape space is limited**
   - Cannot express W/H ratios below ~0.76
   - Some body proportions are outside ANNY's range

2. **SAM-3D mesh artifacts**
   - Clothing affects circumferences (baggy clothes → larger measurements)
   - Pose affects measurements (arms close to body → bust inflation)

3. **Joint extraction is approximate**
   - Left wrist sometimes underestimated
   - Relies on horizontal slicing which may miss joints in unusual poses

## Phase 4: Calibration Regression (TODO)

**Requires:** 550-person dataset with ground truth measurements

Instead of simple scaling, train a regression model:
```
Waist_real = α × Waist_anny + β × BMI_estimated + γ
```

This corrects systematic biases:
- ANNY underestimates waist on curvy body types
- ANNY overestimates bust on certain poses
- etc.

### Implementation Plan for Phase 4

1. Run current pipeline on 550-person dataset
2. Collect (predicted, ground_truth) pairs for each measurement
3. Train linear regressors with features:
   - ANNY measurement
   - Estimated BMI
   - Gender
   - Waist/hip ratio
   - Height
4. Evaluate on held-out test set
5. Deploy calibrated model

## Key Files

| File | Purpose |
|------|---------|
| `src/services/anny_integration.py` | Main ANNY fitting logic |
| `src/services/body_type.py` | Body type classification |
| `src/services/sizing.py` | Bridal size calculation |
| `scripts/evaluate_measurements.py` | Evaluation script |
| `scripts/test_anny_fitting.py` | Single-mesh testing |

## ANNY Phenotype Parameters

ANNY has 6 phenotype parameters (0-1 scale):
- `gender`: 0=male, 1=female
- `age`: 0=young, 1=old
- `height`: 0=short (~1.5m), 1=tall (~2.0m)
- `weight`: 0=thin, 1=heavy
- `muscle`: 0=low muscle, 1=high muscle
- `proportions`: body proportions

## ANNY Pose System (Critical Knowledge)

**Source code location:** `/Users/jonathan/projects/anny/`

### Coordinate Systems (VERIFIED)

| System | +X | -X | +Z | Origin |
|--------|----|----|----|----|
| **ANNY** | Left | Right | Up | Pelvis |
| **SAM-3D** | Right | Left | Up | Mesh center |

**Verified from ANNY template bone positions:**
```
upperarm01.L (Left arm):  X = +0.168  → +X = Left
upperarm01.R (Right arm): X = -0.168  → -X = Right
```

**Verified from SAM-3D joint extraction:**
```
hip_l (Left hip): X = -0.256  → -X = Left
```

**Critical:** When computing target directions from SAM-3D to match ANNY, you must **flip the X component**:
```python
tgt_dir[0] = -tgt_dir[0]  # Convert SAM-3D coords to ANNY coords
```

### Pose Parameterizations

ANNY supports 4 pose parameterizations (see `rigged_model.py` lines 240-263):

| Parameterization | Use Case |
|------------------|----------|
| `rest_relative` | **Use this.** Delta transforms relative to rest pose. No global base transform. |
| `root_relative` | Root bone controls global position via 6DOF |
| `root_relative_world` | Mixed control (position + local rotation) |
| `absolute` | Direct absolute poses |

### World vs Local Rotations

ANNY's `rest_relative` mode expects **local rotations** (in the bone's local frame), not world rotations.

**Basis Change Formula:**
```python
# Convert world rotation W to local rotation L
# L = R_rest^T @ W @ R_rest
local_rot_mat = rest_global_rot.T @ world_rot_mat @ rest_global_rot
local_rotvec = Rotation.from_matrix(local_rot_mat).as_rotvec()
```

Where `rest_global_rot` is the bone's rest pose rotation matrix (3x3 from the 4x4 transform).

### Bone Mapping (ANNY names → Our joint names)

```python
joint_mapping = {
    "pelvis": "root",
    "hip_l": "upperleg01.L",      # NOT pelvis.L (which is at center)
    "hip_r": "upperleg01.R",
    "knee_l": "lowerleg01.L",
    "knee_r": "lowerleg01.R",
    "ankle_l": "foot.L",
    "ankle_r": "foot.R",
    "shoulder_l": "upperarm01.L",
    "shoulder_r": "upperarm01.R",
    "elbow_l": "lowerarm01.L",
    "elbow_r": "lowerarm01.R",
    "wrist_l": "wrist.L",
    "wrist_r": "wrist.R",
    "neck": "neck01",
    "head": "head",
}
```

### Local Bone Rotation Axes (VERIFIED EMPIRICALLY)

**To bring arms IN toward body (from T-pose):**
- Left arm (`upperarm01.L`): **-Z rotation** (negative)
- Right arm (`upperarm01.R`): **+Z rotation** (positive)
- **Z is sensitive** - values above ~25-30° push elbow into body

**To move arm FORWARD/BACKWARD (from T-pose):**
- Right arm (`upperarm01.R`): **+X rotation** = forward, **-X rotation** = backward
- Left arm (`upperarm01.L`): (untested, likely same convention)
- **Note:** This is OPPOSITE to legs where -X = forward

**To twist forearm (palm orientation):**
- Right forearm (`lowerarm01.R`): **+Y rotation** = palm rotates inward (toward face)
- Right forearm (`lowerarm01.R`): **-Y rotation** = palm rotates outward

**"Holding something to face" pose (right arm):**
```python
# Upper arm: forward + slightly inward
"upperarm01.R": rotation_x(+60°) @ rotation_z(+25°)
# Forearm: bend elbow + twist palm toward face
"lowerarm01.R": rotation_x(+90°) @ rotation_y(+45°)
```

**"Hand to neck" pose (right arm):**
```python
"upperarm01.R": rotation_x(+75°) @ rotation_z(+30°)
"lowerarm01.R": rotation_x(+110°)
```

**To bring legs TOGETHER (from rest pose):**
- Left leg (`upperleg01.L`): **+Z rotation** (positive)
- Right leg (`upperleg01.R`): **-Z rotation** (negative)

**To move leg FORWARD/BACKWARD (stepping/walking):**
- Left leg (`upperleg01.L`): **-X rotation** = forward, **+X rotation** = backward
- Right leg (`upperleg01.R`): **-X rotation** = forward, **+X rotation** = backward
- **Same sign for both legs** (unlike inward/outward which is inverted)

**To twist leg INWARD/OUTWARD:**
- Left leg (`upperleg01.L`): **-Y rotation** = outward, **+Y rotation** = inward
- Right leg (`upperleg01.R`): **-Y rotation** = inward, **+Y rotation** = outward
- **Inverted between left and right**

**To tilt head/neck:**
- Neck (`neck01`): **-X rotation** → head tilts BACKWARDS
- Neck (`neck01`): **+X rotation** → head tilts FORWARDS

**Pelvis/Root rotations:**
- **X-axis**: Body tilt forward/backward (+X = head down, -X = head up)
- **Y-axis**: Body twist left/right (+Y = twist right, -Y = twist left)
- **Z-axis**: Hip drop/pelvis tilt (+Z = right hip higher/left lower, -Z = left hip higher/right lower)

**Key insights:**
1. Left and right limbs need **opposite sign** rotations for symmetric movements (Z-axis)
2. Arms and legs have **opposite sign conventions** for "inward" movement (Z-axis)
3. **Legs are more sensitive** - 10° moves legs significantly vs 45° for arms
4. **Arm Z-axis is also sensitive** - above 25-30° pushes elbow into body
5. Neck uses X axis for forward/back tilt
6. **Leg forward/backward (X-axis):** Same sign for both legs (-X = forward)
7. **Arm forward/backward (X-axis):** OPPOSITE to legs (+X = forward for arms)
8. **Leg twist (Y-axis):** Inverted between left and right legs
9. **Forearm Y rotation:** Controls palm orientation (+Y = palm inward toward face)
10. **Complex poses require parent bone rotation:** For unusual limb directions (e.g., tree pose), rotate `pelvis.R`/`pelvis.L` first to orient the entire leg chain, then fine-tune with child bones
11. **pelvis.R Y rotation:** Key for pointing leg inward toward body (+45 to +60°)
12. **foot.R Z rotation:** Swings foot in/out (-30° swings inward toward standing leg)

```python
# Bring arms DOWN/IN:
pose_params['upperarm01.L'] = rotation_around_z(-45°)  # negative
pose_params['upperarm01.R'] = rotation_around_z(+45°)  # positive

# Bring legs TOGETHER:
pose_params['upperleg01.L'] = rotation_around_z(+10°)  # positive (note: opposite sign!)
pose_params['upperleg01.R'] = rotation_around_z(-10°)  # negative

# Step LEFT leg FORWARD (asymmetric stance):
pose_params['upperleg01.L'] = rotation_around_x(-20°)  # negative X = forward
pose_params['upperleg01.R'] = rotation_around_x(+10°)  # positive X = backward (same sign convention)

# Tilt head BACKWARDS:
pose_params['neck01'] = rotation_around_x(-20°)  # negative X
```

### Complex Poses: Hierarchical Bone Control (VERIFIED EMPIRICALLY)

**Key Discovery:** For complex poses where a limb needs to point in an unusual direction, rotating just the limb bone (`upperleg01.R`) is NOT enough. You must rotate the **parent bone** (`pelvis.R`) to orient the entire limb chain first.

**Tree Pose (Vrksasana) - Right Leg Example:**
```python
# Foot resting on inner left thigh, knee pointing outward
"pelvis.R": rotation_x(-10) @ rotation_y(55) @ rotation_z(25)   # Orient hip
"upperleg01.R": rotation_z(25) @ rotation_x(-10)                 # Abduct + lift
"lowerleg01.R": rotation_x(120)                                   # Bend knee
"foot.R": rotation_z(-30)                                         # Swing foot inward
```

**Bone Hierarchy for Legs:**
```
root
└── pelvis.R          ← Controls overall leg orientation (CRITICAL for complex poses)
    └── upperleg01.R  ← Fine-tune: abduction (Z), forward lift (X)
        └── lowerleg01.R  ← Knee bend (X)
            └── foot.R    ← Foot orientation (Z swings in/out)
```

**pelvis.R Rotation Effects (Right leg):**
- **X rotation:** Tilts leg forward/back (-10 to -15 typical)
- **Y rotation:** Twists leg inward/outward (+45 to +60 points leg inward toward body)
- **Z rotation:** Side tilt (+20 to +30 lifts leg)

**Process for Complex Leg Poses:**
1. Start with `pelvis.R` rotations to get rough leg direction
2. Add `upperleg01.R` Z rotation for knee abduction/adduction
3. Add `lowerleg01.R` X rotation for knee bend
4. Add `foot.R` Z rotation to connect foot to target

**Ablation Study Approach:**
When unsure of parameters, generate a grid search over reasonable ranges:
- Start broad (e.g., 50-100 variations)
- Identify promising candidates
- Refine around those values
- Iterate until desired pose achieved

### Rotation Scaling Factors

Computed rotations need scaling to prevent over-rotation:

| Bone Type | Scale | Notes |
|-----------|-------|-------|
| Upper arms | 0.5 | 50% of computed rotation |
| Upper legs | 0.35 | 35% of computed rotation |
| Lower legs | -0.35 | **Negated** - opposite direction |

Why scaling is needed (not fully understood):
1. Joint extraction errors in SAM-3D amplify into rotation errors
2. ANNY's LBS skinning may amplify rotations
3. Possible coordinate system subtleties not fully accounted for

### Kinematic Chain

Forward kinematics formula (from `kinematics.py`):
```python
# Root bone
root_pose = rest_pose @ delta_transform

# Child bone (inherits parent transform)
child_pose = parent_transform @ (rest_pose @ delta_transform)
```

**Implication:** Rotating a parent bone rotates all children. There's no way to rotate a parent without affecting children (that would require inverse kinematics).

### Known Issues

1. **Whole body shifts when rotating bones**
   - Origin is at pelvis, but rotating limbs can shift mesh center of mass
   - ICP alignment afterwards may compound this
   - Attempted fix: anchor pelvis position after posing (not yet working)

2. **Lower legs need opposite rotation**
   - When X-flip is applied, lower legs rotate inward instead of outward
   - Solution: negate the rotation for `lowerleg` bones

3. **Arms affect body rotation perception**
   - Arm rotations can make the whole body appear rotated
   - Scaling arms to 50% helps

### API Usage

```python
# Generate posed mesh
output = model(
    pose_parameters=pose_params,      # [1, num_bones, 4, 4] homogeneous matrices
    phenotype_kwargs=phenotype_dict,  # {'gender': tensor, 'height': tensor, ...}
    pose_parameterization="rest_relative",
    return_bone_ends=True,            # To get bone_heads/bone_tails
)

vertices = output["vertices"]        # [B, V, 3]
bone_heads = output["bone_heads"]    # [B, J, 3] (only if return_bone_ends=True)
```

### Current Best Results

With arm scaling (0.5), leg scaling (0.35), lower leg negation:
- **Bust:** +5.1 cm (6.4% error)
- **Waist:** -0.4 cm (0.5% error)
- **Hips:** +2.0 cm (2.3% error)
- All measurements under 10% error

## Debug Meshes

When running evaluation, debug meshes are saved:
- `debug_sam3d_scaled.ply` - SAM-3D mesh scaled to user height
- `debug_anny_fitted.ply` - ANNY in T-pose with fitted phenotypes
- `debug_anny_posed.ply` - ANNY posed (experimental, not accurate)

## Commands

```bash
# Run evaluation on dataset
uv run python scripts/evaluate_measurements.py --dataset /path/to/dataset

# Test single mesh
uv run python scripts/test_anny_fitting.py mesh.ply 165cm female

# Run API server
uv run uvicorn src.main:app --reload
```

## Architecture Decision Records

### ADR-001: Ratio matching over vertex matching
**Decision:** Match circumference ratios, not vertex positions
**Rationale:** Closest-point vertex matching fails due to pose/topology mismatch between SAM-3D and ANNY. Ratio matching is pose-invariant and topology-agnostic.

### ADR-002: Measure in T-pose
**Decision:** Always extract measurements from ANNY's rest (T-pose) mesh
**Rationale:** Posed meshes have artifacts (armpit occlusion, stomach folds). T-pose provides clean, consistent measurements.

### ADR-003: Defer calibration to Phase 4
**Decision:** Wait for 550-person dataset before implementing regression calibration
**Rationale:** 21-person dataset is too small for robust regression. Current ratio-matching provides reasonable baseline.

## Known Issues & TODO

### SAM-3D Origin Normalization (HIGH PRIORITY)

**Problem:** SAM-3D meshes arrive with different orientations depending on input image angle (front vs side). Our pose fitting assumes a consistent origin but SAM-3D doesn't guarantee this.

**Evidence:**
- Person 11: Front image → 15 joints extracted, excellent fit (ICP 0.046m)
- Person 11: Side image → 8 joints extracted, terrible fit (ICP 0.108m, +50cm bust error)
- Person 12: Front image (asymmetric pose) → poor hip fit (-11.8cm error)
- Person 12: Side image → better hip fit (-6.6cm error)

**Required Work:**
1. Detect SAM-3D mesh orientation from geometry (find front-facing direction)
2. Rotate mesh to canonical orientation (facing +Y or -Y consistently)
3. Center mesh at pelvis/hip midpoint
4. Apply consistent scaling based on user height
5. Only then proceed with ANNY fitting

**Why This Matters:**
- Current empirical corrections (X rotation -3°, Z rotation -5°, translation offset) are tuned for front images
- Side images have completely different orientation → corrections make things worse
- Need orientation-agnostic preprocessing before fitting

### Other TODOs

1. [ ] Acquire 550-person dataset with ground truth
2. [ ] Run evaluation pipeline on full dataset
3. [ ] Implement Phase 4 calibration regression
4. [ ] Evaluate improvement in MAE
5. [ ] Deploy calibrated model to production
