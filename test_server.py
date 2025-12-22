#!/usr/bin/env python3
"""Test script to diagnose server startup issues"""

print("=" * 60)
print("DIAGNOSTIC TEST")
print("=" * 60)

# Test 1: Python version
import sys
print(f"\n1. Python Version: {sys.version}")

# Test 2: Check imports
print("\n2. Testing imports...")
try:
    import fastapi
    print("   ✓ fastapi imported")
except Exception as e:
    print(f"   ✗ fastapi failed: {e}")

try:
    import uvicorn
    print("   ✓ uvicorn imported")
except Exception as e:
    print(f"   ✗ uvicorn failed: {e}")

try:
    import anthropic
    print("   ✓ anthropic imported")
except Exception as e:
    print(f"   ✗ anthropic failed: {e}")

# Test 3: Check config
print("\n3. Testing config...")
try:
    from stitch.config import get_settings
    settings = get_settings()
    print(f"   ✓ Config loaded")
    print(f"   API Key present: {bool(settings.anthropic_api_key and settings.anthropic_api_key != 'your_api_key_here')}")
except Exception as e:
    print(f"   ✗ Config failed: {e}")

# Test 4: Check directories
print("\n4. Checking directories...")
from pathlib import Path
dirs = ['uploads/renders', 'uploads/silhouettes', 'uploads/garments', 'temp']
for d in dirs:
    exists = Path(d).exists()
    print(f"   {'✓' if exists else '✗'} {d}")

# Test 5: Try to import the app
print("\n5. Testing app import...")
try:
    from stitch.main import app
    print("   ✓ FastAPI app imported successfully")
except Exception as e:
    print(f"   ✗ App import failed: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("DIAGNOSTIC COMPLETE")
print("=" * 60)
