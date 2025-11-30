# Novia Body Measurement Service

AI-powered body measurement extraction from photos using HMR 2.0 and SMPL anthropometry.

## Overview

This service takes a photo of a person and extracts body measurements suitable for wedding dress sizing:

- **Bust, Waist, Hips** (primary measurements)
- **Shoulder width, Arm length, Torso length, Inseam**
- **Body type classification** (hourglass, pear, apple, etc.)
- **Bridal size recommendation**

## Architecture

```
Photo → HMR 2.0 (ViT backbone) → SMPL Parameters → SMPL Mesh → Anthropometry → Measurements
```

### Components

1. **HMR 2.0** (`hmr.py`): Regresses SMPL body parameters from a single image
2. **SMPL** (`hmr.py`): Generates 3D mesh from shape/pose parameters
3. **Anthropometry** (`anthropometry.py`): Extracts measurements from mesh vertices
4. **Service** (`service.py`): Combines everything into a simple API
5. **API** (`api.py`): FastAPI endpoints

## Setup

```bash
# Navigate to measurement directory
cd backend/measurement

# Create venv with Python 3.11 (using uv)
uv venv --python 3.11 .venv
source .venv/bin/activate

# Install dependencies
uv pip install -e .
```

### SMPL Model (Optional but Recommended)

For accurate body measurements, you need the SMPL body model:

1. Register at https://smpl.is.tue.mpg.de/ (free for research)
2. Download "SMPL for Python"
3. Extract and copy `basicModel_neutral_lbs_10_207_0_v1.0.0.pkl` to:
   ```
   ~/.cache/novia-measurement/smpl/SMPL_NEUTRAL.pkl
   ```

Or run the helper script:
```bash
python download_smpl.py
```

**Without SMPL**: The service uses a synthetic body model that provides
approximate measurements. Good enough for body type classification and
relative sizing, but less accurate for absolute measurements.

## Usage

### Python API

```python
from measurement import measure

# With user height for accurate scaling
measurements = measure("photo.jpg", user_height_cm=165)

print(f"Bust: {measurements.bust:.1f} cm")
print(f"Waist: {measurements.waist:.1f} cm")
print(f"Hips: {measurements.hips:.1f} cm")
print(f"Body Type: {measurements.body_type.value}")

# Get bridal size recommendation
bridal = measurements.get_bridal_size()
print(f"Recommended Size: {bridal['recommended_size']}")
```

### REST API

```bash
# Start the server
python -m measurement.main

# Or with uvicorn directly
uvicorn measurement.api:app --port 8001
```

Then call the API:

```bash
curl -X POST "http://localhost:8001/measure" \
  -F "image=@photo.jpg" \
  -F "height_cm=165"
```

Response:
```json
{
  "bust_cm": 89.5,
  "waist_cm": 68.2,
  "hips_cm": 95.3,
  "shoulder_width_cm": 38.4,
  "body_type": "hourglass",
  "confidence": 0.85,
  "bridal_size": {
    "recommended_size": 6,
    "size_range": [6, 8],
    "note": "Sizes are approximate. Professional fitting recommended."
  }
}
```

## Testing

```bash
# Run tests (anthropometry only, skips model loading)
python test_measurement.py --skip-model

# Full test with model loading
python test_measurement.py

# Test with a real image
python test_measurement.py /path/to/photo.jpg --height 170
```

## Performance

| Operation | Time (Apple Silicon) | Time (CPU) |
|-----------|---------------------|------------|
| Model loading | ~5-10s (first time) | ~10-20s |
| Image inference | ~2-5s | ~10-30s |
| Measurement extraction | ~100ms | ~100ms |

## Accuracy

- **With user height**: ±2-3 cm for major measurements
- **Without height**: Relative proportions only (body type classification still works)

For wedding dress sizing, we recommend:
1. Always collect user height
2. Present a size *range* not a single size
3. Recommend professional fitting for final purchase

## Notes

- The service uses Apple Silicon MPS acceleration when available
- SMPL model files are downloaded on first use (~50MB)
- ViT-H backbone is loaded from `timm` pretrained weights
