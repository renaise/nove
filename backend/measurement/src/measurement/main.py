"""
Main entry point for the measurement service.
"""

import uvicorn


def main():
    """Run the measurement API server."""
    uvicorn.run(
        "measurement.api:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
    )


if __name__ == "__main__":
    main()
