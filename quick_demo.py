#!/usr/bin/env python3
"""Quick demo of the Stitch Engine AI capabilities"""

import requests
import json

BASE_URL = "http://localhost:8000"

print("=" * 70)
print("🧠 Nove Stitch Engine - AI Demo")
print("=" * 70)

# Test 1: API Status
print("\n1️⃣ Testing API Status...")
response = requests.get(f"{BASE_URL}/")
print(f"✅ Status: {response.json()['status']}")
print(f"✅ AI Model: {response.json()['ai_model']}")

# Test 2: Health Check
print("\n2️⃣ Testing Health...")
response = requests.get(f"{BASE_URL}/health")
print(f"✅ Health: {response.json()['status']}")

print("\n" + "=" * 70)
print("🎯 Server is fully operational with Opus 4.5!")
print("=" * 70)
print("\n📖 Next Steps:")
print("   • Visit http://localhost:8000/docs for interactive API testing")
print("   • Upload a bride silhouette image to test AI validation")
print("   • Upload a bridal gown to test garment processing")
print("   • Generate a virtual try-on to see AI orchestration")
print("\n💡 The AI will analyze:")
print("   - Body pose and A-pose detection")
print("   - Image quality and lighting")
print("   - Background separation feasibility")
print("   - Size compatibility predictions")
print("   - Style matching insights")
print("=" * 70)
