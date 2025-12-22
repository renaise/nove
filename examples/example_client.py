#!/usr/bin/env python3
"""
Example client demonstrating the Nove Stitch Engine API

This script shows how to:
1. Upload and process a bride silhouette
2. Upload and process a boutique garment
3. Generate a virtual try-on render
4. Monitor progress via WebSocket
"""

import requests
import json
import asyncio
import websockets
from pathlib import Path


BASE_URL = "http://localhost:8000"
WS_URL = "ws://localhost:8000/ws"


def check_health():
    """Check if the API is running"""
    print("🔍 Checking API health...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        response.raise_for_status()
        print("✅ API is healthy!")
        print(json.dumps(response.json(), indent=2))
        return True
    except Exception as e:
        print(f"❌ API not available: {e}")
        print("Make sure to run: python run.py")
        return False


def upload_bride_silhouette(image_path: str):
    """Upload bride silhouette image"""
    print(f"\n📤 Uploading bride silhouette: {image_path}")

    if not Path(image_path).exists():
        print(f"❌ File not found: {image_path}")
        return None

    with open(image_path, 'rb') as f:
        files = {'file': f}
        response = requests.post(f"{BASE_URL}/bride/upload", files=files)

    if response.status_code == 200:
        data = response.json()
        print(f"✅ Upload successful! Image ID: {data['image_id']}")
        return data['image_id']
    else:
        print(f"❌ Upload failed: {response.text}")
        return None


def process_bride_silhouette(image_id: str):
    """Process bride silhouette with AI validation"""
    print(f"\n🧠 Processing bride silhouette with Opus 4.5...")

    payload = {
        "image_id": image_id,
        "privacy_mode": True
    }

    response = requests.post(f"{BASE_URL}/bride/process", json=payload)

    if response.status_code == 200:
        data = response.json()
        print(f"✅ Processing complete!")
        print(f"   Silhouette ID: {data['silhouette_id']}")
        print(f"   Status: {data['status']}")

        if data.get('quality'):
            quality = data['quality']
            print(f"   Quality Score: {quality['score']:.2f}")
            print(f"   Valid: {quality['is_valid']}")
            if quality.get('recommendations'):
                print(f"   AI Recommendations: {', '.join(quality['recommendations'][:2])}")

        return data['silhouette_id']
    else:
        print(f"❌ Processing failed: {response.text}")
        return None


def upload_boutique_garment(image_path: str):
    """Upload boutique garment image"""
    print(f"\n📤 Uploading boutique garment: {image_path}")

    if not Path(image_path).exists():
        print(f"❌ File not found: {image_path}")
        return None

    with open(image_path, 'rb') as f:
        files = {'file': f}
        response = requests.post(f"{BASE_URL}/boutique/upload", files=files)

    if response.status_code == 200:
        data = response.json()
        print(f"✅ Upload successful! Image ID: {data['image_id']}")
        return data['image_id']
    else:
        print(f"❌ Upload failed: {response.text}")
        return None


def process_boutique_garment(image_id: str, garment_name: str, boutique_id: str):
    """Process boutique garment with AI validation"""
    print(f"\n🧠 Processing garment '{garment_name}' with Opus 4.5...")

    payload = {
        "image_id": image_id,
        "garment_name": garment_name,
        "boutique_id": boutique_id
    }

    response = requests.post(f"{BASE_URL}/boutique/process", json=payload)

    if response.status_code == 200:
        data = response.json()
        print(f"✅ Processing complete!")
        print(f"   Garment ID: {data['garment_id']}")
        print(f"   Status: {data['status']}")

        if data.get('quality'):
            quality = data['quality']
            print(f"   Quality Score: {quality['score']:.2f}")
            print(f"   Valid: {quality['is_valid']}")

        return data['garment_id']
    else:
        print(f"❌ Processing failed: {response.text}")
        return None


def generate_tryon(silhouette_id: str, garment_id: str):
    """Generate virtual try-on render"""
    print(f"\n✨ Generating virtual try-on with Opus 4.5 orchestration...")

    payload = {
        "silhouette_id": silhouette_id,
        "garment_id": garment_id,
        "render_quality": "standard"
    }

    response = requests.post(f"{BASE_URL}/tryon/process", json=payload)

    if response.status_code == 200:
        data = response.json()
        print(f"✅ Try-on complete!")
        print(f"   Try-On ID: {data['tryon_id']}")
        print(f"   Status: {data['status']}")
        print(f"   Render URL: {BASE_URL}{data['render_url']}")
        print(f"   Processing Time: {data['processing_time_ms']}ms")
        print(f"   AI Analysis: {data['message']}")
        return data
    else:
        print(f"❌ Try-on failed: {response.text}")
        return None


async def monitor_websocket():
    """Monitor WebSocket for real-time updates"""
    print("\n📡 Connecting to WebSocket for real-time updates...")

    try:
        async with websockets.connect(WS_URL) as websocket:
            print("✅ Connected to WebSocket!")
            print("Listening for updates...\n")

            async for message in websocket:
                data = json.loads(message)
                print(f"🔔 WebSocket Update: {data.get('type', 'unknown')}")
                print(f"   {json.dumps(data, indent=2)}\n")

    except Exception as e:
        print(f"WebSocket error: {e}")


def main():
    """Main example flow"""
    print("=" * 70)
    print("🎀 Nove Stitch Engine - Example Client")
    print("=" * 70)

    # Check API health
    if not check_health():
        return

    print("\n" + "=" * 70)
    print("📝 Example Flow:")
    print("   1. Upload bride silhouette")
    print("   2. Process with AI validation")
    print("   3. Upload boutique garment")
    print("   4. Process with AI validation")
    print("   5. Generate virtual try-on")
    print("=" * 70)

    # Example with placeholder images
    print("\n⚠️  Note: This example expects you to provide image paths")
    print("   Replace the paths below with your actual images:\n")

    bride_image = "path/to/bride_silhouette.jpg"
    garment_image = "path/to/bridal_gown.jpg"

    print(f"   Bride Image: {bride_image}")
    print(f"   Garment Image: {garment_image}")
    print("\n   Or test individual endpoints using the API docs:")
    print(f"   👉 {BASE_URL}/docs")

    # Uncomment to run full flow when you have images:
    #
    # # Upload and process bride
    # bride_img_id = upload_bride_silhouette(bride_image)
    # if not bride_img_id:
    #     return
    #
    # silhouette_id = process_bride_silhouette(bride_img_id)
    # if not silhouette_id:
    #     return
    #
    # # Upload and process garment
    # garment_img_id = upload_boutique_garment(garment_image)
    # if not garment_img_id:
    #     return
    #
    # garment_id = process_boutique_garment(
    #     garment_img_id,
    #     "Sample Bridal Gown",
    #     "boutique_demo"
    # )
    # if not garment_id:
    #     return
    #
    # # Generate try-on
    # result = generate_tryon(silhouette_id, garment_id)
    #
    # if result:
    #     print("\n" + "=" * 70)
    #     print("🎉 SUCCESS! Virtual try-on generated")
    #     print("=" * 70)
    #     print(f"\nView the render at: {BASE_URL}{result['render_url']}")

    print("\n" + "=" * 70)
    print("For WebSocket monitoring, run: python examples/websocket_monitor.py")
    print("=" * 70)


if __name__ == "__main__":
    main()
