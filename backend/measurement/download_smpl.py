#!/usr/bin/env python3
"""
Download SMPL model files.

The SMPL body model requires registration at https://smpl.is.tue.mpg.de/
After registration, download the neutral model and place it in the cache directory.

This script provides instructions and sets up the directory structure.
"""

import os
from pathlib import Path

CACHE_DIR = Path.home() / ".cache" / "novia-measurement" / "smpl"


def main():
    print("=" * 60)
    print("SMPL Model Setup")
    print("=" * 60)

    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    smpl_file = CACHE_DIR / "SMPL_NEUTRAL.pkl"

    if smpl_file.exists():
        print(f"\n✓ SMPL model already exists at:")
        print(f"  {smpl_file}")
        return

    print(f"""
The SMPL body model requires registration to download.

Steps to get the SMPL model:

1. Register at: https://smpl.is.tue.mpg.de/
   (Academic/research use is free)

2. After registration, download:
   - "SMPL for Python" package
   - Extract and find: basicModel_neutral_lbs_10_207_0_v1.0.0.pkl

3. Copy or rename the file to:
   {smpl_file}

Alternatively, you can use the synthetic model for testing
(measurements will be approximate but functional).

Cache directory: {CACHE_DIR}
""")

    # Check if user has the file somewhere else
    common_locations = [
        Path.home() / "Downloads" / "basicModel_neutral_lbs_10_207_0_v1.0.0.pkl",
        Path.home() / "Downloads" / "SMPL_NEUTRAL.pkl",
        Path.home() / "Downloads" / "smpl" / "basicModel_neutral_lbs_10_207_0_v1.0.0.pkl",
    ]

    for loc in common_locations:
        if loc.exists():
            print(f"Found SMPL model at: {loc}")
            response = input(f"Copy to cache directory? [y/N] ")
            if response.lower() == 'y':
                import shutil
                shutil.copy(loc, smpl_file)
                print(f"✓ Copied to {smpl_file}")
                return

    print("\nOnce you have the model file, run this script again or")
    print("simply place the file in the cache directory.")


if __name__ == "__main__":
    main()
