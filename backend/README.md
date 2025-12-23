# Novia Backend

AI-powered wedding dress recommendation and body analysis service.

## Features

- **Body Analysis**: Extract 3D body mesh from photos using SAM-3D-Body
- **Body Type Classification**: Classify body types (hourglass, pear, apple, etc.)
- **Silhouette Recommendations**: Recommend flattering dress silhouettes
- **Dress Size Calculation**: Calculate US bridal dress sizes from measurements
- **Dress Matching**: Query dresses by silhouette and size availability
- **Virtual Try-On**: Generate try-on previews using Nano Banana Pro (Gemini)

## Quick Start

### Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) package manager
- Docker & Docker Compose (for development)
- NVIDIA GPU + CUDA 12.1 (for production SAM-3D-Body inference)

### Development Setup

```bash
# Install dependencies
uv sync --dev

# Start database
docker compose up -d db

# Run the API server
uv run uvicorn src.main:app --reload

# Run tests
uv run pytest

# Type check
uv run ty check src/

# Lint
uv run ruff check src/
```

### Docker Development

```bash
# Start all services (API + database)
docker compose up -d

# View logs
docker compose logs -f api

# Stop services
docker compose down
```

## API Endpoints

### Body Analysis

```bash
POST /api/analyze-body
Content-Type: application/json

{
  "images": ["base64_encoded_image"],
  "user_id": "optional_user_id"
}
```

### Dress Recommendations

```bash
POST /api/get-dress-recommendations
Content-Type: application/json

{
  "silhouettes": ["mermaid", "a-line"],
  "user_size": 8,
  "price_range": {"min": 1000, "max": 3000},
  "limit": 10
}
```

### Try-On Generation

```bash
POST /api/generate-tryon
Content-Type: application/json

{
  "user_photo": "base64_or_url",
  "dress_id": "dress_123"
}
```

### Reference Endpoints

- `GET /api/silhouettes` - List all silhouette types
- `GET /api/size-chart` - Get bridal sizing chart
- `GET /api/health` - Health check

## Architecture

```
src/
├── main.py              # FastAPI app entry
├── config.py            # Environment configuration
├── api/
│   ├── routes.py        # API endpoints
│   └── schemas.py       # Pydantic models
├── services/
│   ├── body_analysis.py # SAM-3D-Body integration
│   ├── body_type.py     # Body type classification
│   ├── silhouette.py    # Silhouette recommendations
│   ├── sizing.py        # Dress size calculation
│   ├── dress_matcher.py # Database queries
│   └── tryon_generator.py # Gemini integration
├── models/
│   └── database.py      # SQLAlchemy models
└── utils/
    ├── mesh_utils.py    # 3D mesh processing
    └── image_utils.py   # Image preprocessing
```

## Configuration

Environment variables (prefix: `NOVIA_`):

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | Required |
| `GEMINI_API_KEY` | Google Gemini API key | Required for try-on |
| `AWS_REGION` | AWS region for S3 | `us-east-1` |
| `S3_BUCKET` | S3 bucket for assets | `novia-assets` |
| `SAM3D_CHECKPOINT_PATH` | Path to SAM-3D-Body model | `./checkpoints/...` |
| `DEBUG` | Enable debug mode | `false` |

## Important: SAM-3D Measurement Limitations

**SAM-3D absolute measurements cannot be trusted.** The mesh has no real-world scale reference - it only captures the **relative shape/silhouette** of the person.

### What SAM-3D provides:
- ✅ Relative body proportions (waist/hip ratio, bust/hip ratio)
- ✅ Body silhouette shape
- ✅ Anatomical landmark positions (relative)

### What SAM-3D does NOT provide:
- ❌ Absolute measurements in cm/inches
- ❌ Actual height (mesh height varies by camera distance/angle)
- ❌ Actual weight

### How we extract real measurements:

1. **User provides**: height (required) + gender (required)
2. **SAM-3D provides**: body shape ratios from mesh
3. **ANNY fitting**: matches ANNY parametric model to SAM-3D shape ratios
4. **Scale**: ANNY mesh is scaled to user's actual height
5. **Output**: real-world measurements from scaled ANNY model

### Dynamic Position Finding

We don't use fixed height percentages for bust/waist/hips. Instead, we scan the mesh:
- **Bust**: where arms split off (1 loop → 3 loops transition)
- **Waist**: narrowest torso point between bust and hips
- **Hips**: widest point in the pelvis region (max perimeter)

This adapts to different poses and body types.

### Expected Accuracy

With proper input (form-fitting clothing, good pose, accurate height/gender):
- **~5-7cm MAE** for bust/waist/hips
- **~1-2 dress sizes** accuracy

Accuracy degrades with: baggy clothing, unusual poses, inaccurate height input.

## Model Setup (SAM-3D-Body)

```bash
# Download SAM-3D-Body checkpoints
hf download facebook/sam-3d-body-dinov3 --local-dir checkpoints/sam-3d-body-dinov3

# Structure:
# checkpoints/
#   sam-3d-body-dinov3/
#     model.ckpt
#     assets/
#       mhr_model.pt
```

## License

Proprietary - Novia Inc.
