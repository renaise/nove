#!/usr/bin/env python3
"""
Evaluate ANNY body measurements against ground truth dataset.

Usage:
    python scripts/evaluate_measurements.py --dataset /path/to/body-measurements-dataset

Outputs a comparison table and error statistics.
"""

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import trimesh

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from services.anny_integration import ANNYBodyAnalyzer


def load_ground_truth(person_dir: Path) -> dict | None:
    """Load ground truth measurements from JSON files in person directory."""
    # Try different possible JSON file names
    for name in ["measurements.json", "data.json", "info.json", "body.json"]:
        json_path = person_dir / name
        if json_path.exists():
            with open(json_path) as f:
                return json.load(f)
    return None


def parse_measurement(value: str | float | None) -> float | None:
    """Parse a measurement value, handling strings with units or markers."""
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    # Handle strings like "70.0_tbr" or "68.0 cm"
    value = str(value).lower().replace("cm", "").replace("_tbr", "").strip()
    try:
        return float(value)
    except ValueError:
        return None


def run_evaluation(dataset_path: Path, limit: int | None = None, skip_missing: bool = True, person_id: str | None = None, use_side: bool = False):
    """Run evaluation on all people in dataset."""

    files_dir = dataset_path / "files"
    if not files_dir.exists():
        print(f"Error: {files_dir} not found")
        sys.exit(1)

    # Find all person directories with meshes
    person_dirs = sorted([d for d in files_dir.iterdir() if d.is_dir()])

    # Filter to specific person if requested
    if person_id is not None:
        person_dirs = [d for d in person_dirs if d.name == person_id]
        if not person_dirs:
            print(f"Error: Person '{person_id}' not found in dataset")
            sys.exit(1)
    elif limit:
        person_dirs = person_dirs[:limit]

    mesh_name = "mesh_side.ply" if use_side else "mesh.ply"
    print(f"Found {len(person_dirs)} people to evaluate")
    print(f"Using mesh: {mesh_name}")
    print()

    # Initialize ANNY analyzer (lazy loads model on first use)
    analyzer = ANNYBodyAnalyzer(device="cpu")

    results = []
    errors = {
        "bust": [],
        "waist": [],
        "hips": [],
        "weight": [],
    }

    for i, person_dir in enumerate(person_dirs):
        person_id = person_dir.name
        mesh_path = person_dir / mesh_name

        if not mesh_path.exists():
            if skip_missing:
                continue
            print(f"[{i+1}] {person_id}: No mesh.ply found, skipping")
            continue

        # Load ground truth
        gt = load_ground_truth(person_dir)
        if not gt:
            print(f"[{i+1}] {person_id}: No ground truth JSON found, skipping")
            continue

        # Parse ground truth values
        gt_height = parse_measurement(gt.get("height"))
        gt_bust = parse_measurement(gt.get("chest_circumference_cm"))
        gt_waist = parse_measurement(gt.get("waist_circumference_cm"))
        # Prefer pelvis_circumference (more reliable), fallback to hips_circumference
        gt_hips = parse_measurement(gt.get("pelvis_circumference_cm")) or parse_measurement(gt.get("hips_circumference_cm"))
        gt_weight = parse_measurement(gt.get("weight"))
        gt_gender = gt.get("gender")  # 'male' or 'female'

        if gt_height is None:
            print(f"[{i+1}] {person_id}: No height in ground truth, skipping")
            continue

        print(f"[{i+1}/{len(person_dirs)}] {person_id} (GT height: {gt_height} cm)")

        try:
            # Load mesh and run ANNY analysis
            mesh = trimesh.load(str(mesh_path))
            vertices = np.array(mesh.vertices, dtype=np.float32)
            faces = np.array(mesh.faces, dtype=np.int32) if hasattr(mesh, 'faces') else None

            # Save debug meshes for visual comparison
            debug_prefix = str(person_dir / "debug")

            result = analyzer.analyze_from_vertices(
                vertices,
                user_height_cm=gt_height,
                user_gender=gt_gender,
                faces=faces,
                save_debug_meshes=debug_prefix,
            )
            m = result.measurements
            print(f"  Saved meshes: debug_sam3d_scaled.ply, debug_anny_fitted.ply")

            # Calculate errors
            bust_err = m.bust_cm - gt_bust if gt_bust else None
            waist_err = m.waist_cm - gt_waist if gt_waist else None
            hips_err = m.hips_cm - gt_hips if gt_hips else None
            weight_err = m.weight_kg - gt_weight if gt_weight else None

            # Store results
            row = {
                "person_id": person_id,
                "gt_height": gt_height,
                "gt_bust": gt_bust,
                "gt_waist": gt_waist,
                "gt_hips": gt_hips,
                "gt_weight": gt_weight,
                "pred_bust": m.bust_cm,
                "pred_waist": m.waist_cm,
                "pred_hips": m.hips_cm,
                "pred_weight": m.weight_kg,
                "bust_err": bust_err,
                "waist_err": waist_err,
                "hips_err": hips_err,
                "weight_err": weight_err,
                "confidence": result.confidence,
                "phenotypes": result.phenotypes,
            }
            results.append(row)

            # Accumulate errors for statistics
            if bust_err is not None:
                errors["bust"].append(bust_err)
            if waist_err is not None:
                errors["waist"].append(waist_err)
            if hips_err is not None:
                errors["hips"].append(hips_err)
            if weight_err is not None:
                errors["weight"].append(weight_err)

            # Print row
            print(f"  Bust:   {m.bust_cm:5.1f} cm (GT: {gt_bust or '?':>5}, err: {bust_err:+6.1f} cm)" if bust_err else f"  Bust:   {m.bust_cm:5.1f} cm (GT: N/A)")
            print(f"  Waist:  {m.waist_cm:5.1f} cm (GT: {gt_waist or '?':>5}, err: {waist_err:+6.1f} cm)" if waist_err else f"  Waist:  {m.waist_cm:5.1f} cm (GT: N/A)")
            print(f"  Hips:   {m.hips_cm:5.1f} cm (GT: {gt_hips or '?':>5}, err: {hips_err:+6.1f} cm)" if hips_err else f"  Hips:   {m.hips_cm:5.1f} cm (GT: N/A)")
            print(f"  Weight: {m.weight_kg:5.1f} kg (GT: {gt_weight or '?':>5}, err: {weight_err:+6.1f} kg)" if weight_err else f"  Weight: {m.weight_kg:5.1f} kg (GT: N/A)")
            print()

        except Exception as e:
            print(f"  [ERROR] {e}")
            print()
            continue

    # Print summary statistics
    print()
    print("=" * 60)
    print("EVALUATION SUMMARY")
    print("=" * 60)
    print(f"Total evaluated: {len(results)}")
    print()

    print("Error Statistics (Predicted - Ground Truth):")
    print("-" * 60)
    print(f"{'Measurement':<12} {'N':>4} {'Mean':>8} {'Std':>8} {'MAE':>8} {'Min':>8} {'Max':>8}")
    print("-" * 60)

    for name, errs in errors.items():
        if len(errs) > 0:
            errs = np.array(errs)
            unit = "kg" if name == "weight" else "cm"
            print(f"{name.capitalize():<12} {len(errs):>4} {errs.mean():>+7.1f} {errs.std():>7.1f} {np.abs(errs).mean():>7.1f} {errs.min():>+7.1f} {errs.max():>+7.1f} {unit}")

    print("-" * 60)
    print()

    # Percentage errors
    print("Percentage Errors (|error| / GT * 100):")
    print("-" * 60)

    for name in ["bust", "waist", "hips"]:
        pct_errors = []
        for r in results:
            gt_val = r.get(f"gt_{name}")
            err = r.get(f"{name}_err")
            if gt_val and err and gt_val > 0:
                pct_errors.append(abs(err) / gt_val * 100)
        if pct_errors:
            pct_errors = np.array(pct_errors)
            print(f"{name.capitalize():<12} Mean: {pct_errors.mean():5.1f}%  Median: {np.median(pct_errors):5.1f}%  <10%: {(pct_errors < 10).sum()}/{len(pct_errors)}")

    print()

    # Save detailed results to JSON
    output_path = dataset_path / "evaluation_results.json"
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"Detailed results saved to: {output_path}")

    # Also save as CSV for easy viewing
    csv_path = dataset_path / "evaluation_results.csv"
    with open(csv_path, "w") as f:
        headers = ["person_id", "gt_height", "gt_bust", "gt_waist", "gt_hips", "gt_weight",
                   "pred_bust", "pred_waist", "pred_hips", "pred_weight",
                   "bust_err", "waist_err", "hips_err", "weight_err", "confidence"]
        f.write(",".join(headers) + "\n")
        for r in results:
            row = [str(r.get(h, "")) for h in headers]
            f.write(",".join(row) + "\n")
    print(f"CSV results saved to: {csv_path}")


def main():
    parser = argparse.ArgumentParser(description="Evaluate ANNY measurements against ground truth")
    parser.add_argument("--dataset", type=Path, required=True, help="Path to body-measurements-dataset")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of people to evaluate")
    parser.add_argument("--person", type=str, default=None, help="Specific person ID to evaluate (e.g., '17')")
    parser.add_argument("--use-side", action="store_true", help="Use side mesh (mesh_side.ply) instead of front")
    args = parser.parse_args()

    run_evaluation(args.dataset, limit=args.limit, person_id=args.person, use_side=args.use_side)


if __name__ == "__main__":
    main()
