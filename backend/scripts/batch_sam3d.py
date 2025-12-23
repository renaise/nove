#!/usr/bin/env python3
"""
Batch process images through SAM-3D-Body to generate PLY meshes.

Setup (one-time):
    # Clone SAM-3D-Body
    git clone https://github.com/facebookresearch/sam-3d-body.git
    cd sam-3d-body
    pip install -e .

    # Download checkpoints
    hf download facebook/sam-3d-body-dinov3 --local-dir checkpoints/sam-3d-body-dinov3

Usage:
    python scripts/batch_sam3d.py --dataset /path/to/body-measurements-dataset

Or use fal.ai API (faster, no local GPU needed):
    python scripts/batch_sam3d.py --dataset /path/to/body-measurements-dataset --use-fal
"""

import argparse
import asyncio
import base64
import json
import os
import sys
from pathlib import Path

# Check for fal client
try:
    import fal_client
    FAL_AVAILABLE = True
except ImportError:
    FAL_AVAILABLE = False


def find_front_image(person_dir: Path) -> Path | None:
    """Find the front-facing image in a person's directory."""
    candidates = [
        "front_img.jpg",
        "front_img.png",
        "front.jpg",
        "front.png",
        "1.jpg",
        "1.png",
    ]
    for name in candidates:
        path = person_dir / name
        if path.exists():
            return path

    # Fallback: first image file
    for ext in ["*.jpg", "*.jpeg", "*.png"]:
        images = list(person_dir.glob(ext))
        if images:
            return images[0]
    return None


def find_side_image(person_dir: Path) -> Path | None:
    """Find the side-facing image in a person's directory."""
    candidates = [
        "side_img.jpg",
        "side_img.png",
        "side.jpg",
        "side.png",
    ]
    for name in candidates:
        path = person_dir / name
        if path.exists():
            return path
    return None


def load_ground_truth(person_dir: Path) -> dict | None:
    """Load ground truth measurements from JSON."""
    json_path = person_dir / "measurements.json"
    if not json_path.exists():
        # Try alternate names
        for name in ["data.json", "info.json", "body.json"]:
            alt_path = person_dir / name
            if alt_path.exists():
                json_path = alt_path
                break

    if json_path.exists():
        with open(json_path) as f:
            return json.load(f)
    return None


async def process_with_fal(image_path: Path, output_dir: Path, mesh_name: str = "mesh.ply") -> dict | None:
    """Process image using fal.ai SAM-3D-Body API."""
    if not FAL_AVAILABLE:
        print("  [ERROR] fal_client not installed. Run: pip install fal-client")
        return None

    # Read and encode image
    with open(image_path, "rb") as f:
        image_data = base64.b64encode(f.read()).decode("utf-8")

    ext = image_path.suffix.lower()
    mime_type = "image/jpeg" if ext in [".jpg", ".jpeg"] else "image/png"
    data_url = f"data:{mime_type};base64,{image_data}"

    try:
        # Call fal.ai API
        result = await fal_client.run_async(
            "fal-ai/sam-3/3d-body",
            arguments={"image_url": data_url, "export_meshes": True}
        )

        # Download PLY mesh
        if "meshes" in result and len(result["meshes"]) > 0:
            mesh_url = result["meshes"][0]["url"]

            import httpx
            async with httpx.AsyncClient() as client:
                response = await client.get(mesh_url)
                response.raise_for_status()

                ply_path = output_dir / mesh_name
                with open(ply_path, "wb") as f:
                    f.write(response.content)

                return {
                    "ply_path": str(ply_path),
                    "metadata": result.get("metadata", {}),
                }

        return None

    except Exception as e:
        print(f"  [ERROR] fal.ai API error: {e}")
        return None


def process_with_local_sam3d(image_path: Path, output_dir: Path, sam3d_path: Path) -> dict | None:
    """Process image using local SAM-3D-Body installation."""
    import subprocess

    checkpoint_path = sam3d_path / "checkpoints/sam-3d-body-dinov3/model.ckpt"
    mhr_path = sam3d_path / "checkpoints/sam-3d-body-dinov3/assets/mhr_model.pt"

    if not checkpoint_path.exists():
        print(f"  [ERROR] Checkpoint not found: {checkpoint_path}")
        print("  Run: hf download facebook/sam-3d-body-dinov3 --local-dir checkpoints/sam-3d-body-dinov3")
        return None

    # Create temp input folder with single image
    import tempfile
    import shutil

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_input = Path(tmpdir) / "input"
        tmp_output = Path(tmpdir) / "output"
        tmp_input.mkdir()
        tmp_output.mkdir()

        # Copy image
        shutil.copy(image_path, tmp_input / image_path.name)

        # Run SAM-3D-Body demo.py
        cmd = [
            sys.executable, str(sam3d_path / "demo.py"),
            "--image_folder", str(tmp_input),
            "--output_folder", str(tmp_output),
            "--checkpoint_path", str(checkpoint_path),
            "--mhr_path", str(mhr_path),
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            if result.returncode != 0:
                print(f"  [ERROR] SAM-3D failed: {result.stderr}")
                return None

            # Find output PLY
            ply_files = list(tmp_output.glob("**/*.ply"))
            if ply_files:
                ply_path = output_dir / "mesh.ply"
                shutil.copy(ply_files[0], ply_path)
                return {"ply_path": str(ply_path)}

            print("  [ERROR] No PLY output found")
            return None

        except subprocess.TimeoutExpired:
            print("  [ERROR] SAM-3D timed out (>5 min)")
            return None


async def main():
    parser = argparse.ArgumentParser(description="Batch process images through SAM-3D-Body")
    parser.add_argument("--dataset", type=Path, required=True, help="Path to body-measurements-dataset")
    parser.add_argument("--use-fal", action="store_true", help="Use fal.ai API instead of local")
    parser.add_argument("--use-side", action="store_true", help="Use side images instead of front")
    parser.add_argument("--person", type=str, default=None, help="Process specific person ID only")
    parser.add_argument("--sam3d-path", type=Path, default=Path.home() / "sam-3d-body",
                        help="Path to local sam-3d-body repo")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of people to process")
    parser.add_argument("--skip-existing", action="store_true", help="Skip if mesh.ply already exists")
    args = parser.parse_args()

    files_dir = args.dataset / "files"
    if not files_dir.exists():
        print(f"Error: {files_dir} not found")
        sys.exit(1)

    # Find all person directories
    person_dirs = sorted([d for d in files_dir.iterdir() if d.is_dir()])

    # Filter to specific person if requested
    if args.person:
        person_dirs = [d for d in person_dirs if d.name == args.person]
        if not person_dirs:
            print(f"Error: Person '{args.person}' not found in dataset")
            sys.exit(1)
    elif args.limit:
        person_dirs = person_dirs[:args.limit]

    image_type = "side" if args.use_side else "front"
    mesh_name = "mesh_side.ply" if args.use_side else "mesh.ply"

    print(f"Found {len(person_dirs)} people to process")
    print(f"Mode: {'fal.ai API' if args.use_fal else 'Local SAM-3D-Body'}")
    print(f"Image type: {image_type}")
    print(f"Output: {mesh_name}")
    print()

    results = []

    for i, person_dir in enumerate(person_dirs):
        person_id = person_dir.name
        print(f"[{i+1}/{len(person_dirs)}] Processing {person_id}...")

        # Check if already processed
        mesh_path = person_dir / mesh_name
        if args.skip_existing and mesh_path.exists():
            print(f"  [SKIP] {mesh_name} already exists")
            continue

        # Find image based on type
        if args.use_side:
            image_path = find_side_image(person_dir)
            if not image_path:
                print("  [SKIP] No side image found")
                continue
        else:
            image_path = find_front_image(person_dir)
            if not image_path:
                print("  [SKIP] No front image found")
                continue

        print(f"  Image: {image_path.name}")

        # Load ground truth
        gt = load_ground_truth(person_dir)
        if gt:
            height = gt.get("height", "?")
            print(f"  Ground truth height: {height} cm")

        # Process
        if args.use_fal:
            result = await process_with_fal(image_path, person_dir, mesh_name)
        else:
            result = process_with_local_sam3d(image_path, person_dir, args.sam3d_path)

        if result:
            print(f"  [OK] Saved: {result['ply_path']}")
            results.append({
                "person_id": person_id,
                "image": str(image_path),
                "mesh": result["ply_path"],
                "ground_truth": gt,
            })
        else:
            print("  [FAIL] No mesh generated")

        print()

    # Save results index
    index_path = args.dataset / "mesh_index.json"
    with open(index_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Saved index to {index_path}")
    print(f"Successfully processed: {len(results)}/{len(person_dirs)}")


if __name__ == "__main__":
    asyncio.run(main())
