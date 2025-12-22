#!/usr/bin/env python3
"""
WebSocket monitor for real-time Stitch Engine updates
"""

import asyncio
import websockets
import json
from datetime import datetime


WS_URL = "ws://localhost:8000/ws"


async def monitor():
    """Connect to WebSocket and monitor updates"""
    print("=" * 70)
    print("📡 Nove Stitch Engine - WebSocket Monitor")
    print("=" * 70)
    print(f"Connecting to: {WS_URL}\n")

    try:
        async with websockets.connect(WS_URL) as websocket:
            print("✅ Connected!")
            print("Listening for real-time updates...")
            print("-" * 70)

            async for message in websocket:
                timestamp = datetime.now().strftime("%H:%M:%S")
                data = json.loads(message)

                # Format the update nicely
                update_type = data.get('type', 'unknown')
                print(f"\n[{timestamp}] 🔔 {update_type.upper()}")

                for key, value in data.items():
                    if key != 'type':
                        print(f"   {key}: {value}")

                print("-" * 70)

    except websockets.exceptions.WebSocketException as e:
        print(f"\n❌ WebSocket error: {e}")
        print("\nMake sure the Stitch Engine is running:")
        print("   python run.py")
    except KeyboardInterrupt:
        print("\n\n👋 Disconnected")


if __name__ == "__main__":
    asyncio.run(monitor())
