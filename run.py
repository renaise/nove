#!/usr/bin/env python3
"""
Nove Stitch Engine - Development Server
"""

import uvicorn
from stitch.config import get_settings

if __name__ == "__main__":
    settings = get_settings()

    print("=" * 60)
    print("🎀 Nove Stitch Engine - Virtual Try-On Pipeline")
    print("=" * 60)
    print(f"AI Model: {settings.anthropic_model}")
    print(f"Server: http://{settings.host}:{settings.port}")
    print(f"API Docs: http://{settings.host}:{settings.port}/docs")
    print(f"WebSocket: ws://{settings.host}:{settings.port}/ws")
    print("=" * 60)
    print()

    uvicorn.run(
        "stitch.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info"
    )
