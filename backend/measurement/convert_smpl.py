#!/usr/bin/env python3
"""
Convert SMPL pickle to numpy-only format (removes chumpy dependency).

Usage:
    python convert_smpl.py /path/to/basicModel_f_lbs_10_207_0_v1.0.0.pkl

This creates a .npz file that can be loaded without chumpy.
"""

import sys
import pickle
import numpy as np
from pathlib import Path


class FakeModule:
    """Fake module to intercept chumpy imports during unpickling."""
    def __init__(self, *args, **kwargs):
        pass

    def __call__(self, *args, **kwargs):
        return self

    def __getattr__(self, name):
        return self


class ChumpyArrayWrapper:
    """Wrapper that captures chumpy arrays and converts to numpy."""
    def __init__(self, data):
        if hasattr(data, 'r'):
            # chumpy array - get the underlying numpy array
            self.data = np.array(data.r)
        else:
            self.data = np.array(data)


class SMPLUnpickler(pickle.Unpickler):
    """Custom unpickler that handles chumpy objects."""

    def find_class(self, module, name):
        # Intercept chumpy imports
        if 'chumpy' in module:
            return FakeModule
        return super().find_class(module, name)


def convert_to_numpy(obj, depth=0):
    """Recursively convert chumpy arrays to numpy."""
    if depth > 10:
        return obj

    if hasattr(obj, 'r'):
        # chumpy Ch array - get the underlying value
        try:
            return np.array(obj.r)
        except:
            return np.array(obj)
    elif hasattr(obj, 'toarray'):
        # scipy sparse matrix
        return np.array(obj.toarray())
    elif hasattr(obj, 'todense'):
        # scipy sparse matrix
        return np.array(obj.todense())
    elif isinstance(obj, np.ndarray):
        # Check if elements are chumpy objects
        if obj.dtype == object and len(obj) > 0:
            try:
                if hasattr(obj.flat[0], 'r'):
                    return np.array([convert_to_numpy(x, depth+1) for x in obj.flat]).reshape(obj.shape)
            except:
                pass
        return obj
    elif isinstance(obj, dict):
        return {k: convert_to_numpy(v, depth+1) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return type(obj)(convert_to_numpy(v, depth+1) for v in obj)
    else:
        return obj


def load_smpl_with_workaround(pkl_path: str) -> dict:
    """Load SMPL pickle with workaround for chumpy."""

    # First, try loading with a workaround using numpy's compatibility
    import io

    with open(pkl_path, 'rb') as f:
        content = f.read()

    # Try standard pickle with encoding
    try:
        data = pickle.loads(content, encoding='latin1')
        return convert_to_numpy(data)
    except ModuleNotFoundError as e:
        if 'chumpy' not in str(e):
            raise

    # If chumpy is missing, we need to mock it
    print("Mocking chumpy for SMPL loading...")

    # Create a fake chumpy module
    import types
    fake_chumpy = types.ModuleType('chumpy')
    fake_chumpy.Ch = type('Ch', (), {
        '__init__': lambda self, *a, **kw: None,
        '__array__': lambda self: np.zeros(1),
        'r': property(lambda self: np.zeros(1)),
    })
    fake_chumpy.ch = fake_chumpy

    # Also need chumpy.ch
    fake_ch = types.ModuleType('chumpy.ch')
    fake_ch.Ch = fake_chumpy.Ch

    sys.modules['chumpy'] = fake_chumpy
    sys.modules['chumpy.ch'] = fake_ch

    try:
        data = pickle.loads(content, encoding='latin1')
        return convert_to_numpy(data)
    finally:
        # Clean up
        del sys.modules['chumpy']
        del sys.modules['chumpy.ch']


def main():
    if len(sys.argv) < 2:
        print("Usage: python convert_smpl.py <smpl_pkl_path>")
        print("\nThis converts SMPL pickle to numpy format.")
        sys.exit(1)

    pkl_path = Path(sys.argv[1])

    if not pkl_path.exists():
        print(f"Error: File not found: {pkl_path}")
        sys.exit(1)

    print(f"Loading SMPL from: {pkl_path}")

    try:
        data = load_smpl_with_workaround(str(pkl_path))
    except Exception as e:
        print(f"Error loading pickle: {e}")
        sys.exit(1)

    print(f"Loaded keys: {list(data.keys())}")

    # Extract the arrays we need
    output = {}

    # Required arrays
    required_keys = {
        'v_template': 'v_template',
        'shapedirs': 'shapedirs',
        'J_regressor': 'J_regressor',
        'weights': 'lbs_weights',
        'kintree_table': 'kintree_table',
        'f': 'faces',
    }

    for src_key, dst_key in required_keys.items():
        if src_key in data:
            arr = data[src_key]

            # Handle various array types
            if hasattr(arr, 'toarray'):
                arr = arr.toarray()
            elif hasattr(arr, 'todense'):
                arr = np.array(arr.todense())
            elif hasattr(arr, 'r'):
                # chumpy array
                arr = np.array(arr.r)

            # Handle object arrays (may contain chumpy arrays)
            arr = np.array(arr)
            if arr.dtype == object:
                # Try to extract numeric data
                try:
                    if hasattr(arr.flat[0], 'r'):
                        arr = np.array([np.array(x.r) for x in arr.flat])
                    else:
                        arr = np.array([np.array(x) for x in arr.flat])
                    # Reshape if possible
                    if src_key == 'shapedirs':
                        # shapedirs should be (6890, 3, 10)
                        arr = arr.reshape(6890, 3, -1)
                except Exception as e:
                    print(f"  Warning: Could not fully convert {src_key}: {e}")

            output[dst_key] = arr
            print(f"  {dst_key}: {output[dst_key].shape} (dtype: {output[dst_key].dtype})")

    # Extract parents from kintree_table
    if 'kintree_table' in output:
        output['parents'] = output['kintree_table'][0]
        del output['kintree_table']

    # Save to cache directory
    cache_dir = Path.home() / ".cache" / "novia-measurement" / "smpl"
    cache_dir.mkdir(parents=True, exist_ok=True)

    output_path = cache_dir / "smpl_params.npz"
    np.savez(output_path, **output)

    print(f"\n✓ Saved to: {output_path}")
    print("  You can now run the measurement service!")


if __name__ == "__main__":
    main()
