# Nove V1 - Setup Guide

## Quick Start

### 1. Prerequisites

- Python 3.11+
- Anthropic API key ([get one here](https://console.anthropic.com/))

### 2. Installation

```bash
# Clone the repository
git clone <repository-url>
cd nove

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your API key
# ANTHROPIC_API_KEY=sk-ant-...
```

### 4. Run the Server

```bash
# Start the Stitch Engine
python run.py

# Or use uvicorn directly
uvicorn stitch.main:app --reload
```

The server will start at: **http://localhost:8000**

### 5. Access API Documentation

Open your browser to:
- **Interactive API Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

---

## Testing the API

### Option 1: Using the Interactive Docs

1. Go to http://localhost:8000/docs
2. Click "Try it out" on any endpoint
3. Upload images and test the pipeline

### Option 2: Using cURL

See examples in `API.md`

### Option 3: Using Python

```python
import requests

# Health check
response = requests.get("http://localhost:8000/health")
print(response.json())
```

---

## Project Structure

```
nove/
├── README.md              # Project overview
├── SETUP.md              # This file
├── API.md                # API documentation
├── requirements.txt      # Python dependencies
├── run.py               # Development server
├── .env                 # Configuration (create from .env.example)
│
├── stitch/              # Main application
│   ├── main.py          # FastAPI app & endpoints
│   ├── config.py        # Configuration management
│   ├── models.py        # Pydantic models
│   ├── orchestrator.py  # Opus 4.5 AI orchestration
│   │
│   ├── pipelines/       # Processing pipelines
│   │   ├── bride.py     # Bride silhouette pipeline
│   │   ├── boutique.py  # Boutique garment pipeline
│   │   └── tryon.py     # Virtual try-on pipeline
│   │
│   └── utils/           # Utilities
│       └── image.py     # Image processing helpers
│
├── tests/               # Test suite
│   └── test_api.py
│
├── uploads/             # Processed images (auto-created)
│   ├── silhouettes/
│   ├── garments/
│   └── renders/
│
└── temp/                # Temporary uploads (auto-created)
```

---

## Development Workflow

### 1. Bride Silhouette Processing

```bash
# Upload
curl -X POST http://localhost:8000/bride/upload \
  -F "file=@path/to/bride.jpg"

# Process with AI
curl -X POST http://localhost:8000/bride/process \
  -H "Content-Type: application/json" \
  -d '{"image_id": "YOUR_IMAGE_ID", "privacy_mode": true}'
```

### 2. Boutique Garment Processing

```bash
# Upload
curl -X POST http://localhost:8000/boutique/upload \
  -F "file=@path/to/dress.jpg"

# Process with AI
curl -X POST http://localhost:8000/boutique/process \
  -H "Content-Type: application/json" \
  -d '{
    "image_id": "YOUR_IMAGE_ID",
    "garment_name": "Lace A-Line Gown",
    "boutique_id": "boutique_001"
  }'
```

### 3. Virtual Try-On

```bash
curl -X POST http://localhost:8000/tryon/process \
  -H "Content-Type: application/json" \
  -d '{
    "silhouette_id": "SILHOUETTE_ID",
    "garment_id": "GARMENT_ID",
    "render_quality": "standard"
  }'
```

---

## WebSocket Connection

```javascript
// Connect to real-time updates
const ws = new WebSocket('ws://localhost:8000/ws');

ws.onopen = () => {
  console.log('Connected to Stitch Engine');
};

ws.onmessage = (event) => {
  const update = JSON.parse(event.data);
  console.log('Processing update:', update);
};
```

---

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=stitch

# Run specific test file
pytest tests/test_api.py
```

---

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `ANTHROPIC_API_KEY` | Anthropic API key | *(required)* |
| `ANTHROPIC_MODEL` | Claude model to use | `claude-opus-4-5-20251101` |
| `HOST` | Server host | `0.0.0.0` |
| `PORT` | Server port | `8000` |
| `DEBUG` | Debug mode | `false` |
| `UPLOAD_DIR` | Upload directory | `./uploads` |
| `TEMP_DIR` | Temp directory | `./temp` |
| `MAX_IMAGE_SIZE_MB` | Max image size | `10` |
| `MAX_IMAGE_DIMENSION` | Max image dimension | `4096` |

---

## Troubleshooting

### "Module not found" errors

```bash
# Make sure you're in the virtual environment
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### "API key not found" errors

```bash
# Check your .env file exists
ls -la .env

# Verify the key is set
cat .env | grep ANTHROPIC_API_KEY
```

### Port already in use

```bash
# Change the port in .env
PORT=8001

# Or run with custom port
uvicorn stitch.main:app --port 8001
```

---

## Next Steps

1. ✅ **You're running!** The prototype is operational
2. 📖 Read `API.md` for detailed API documentation
3. 🧪 Test the endpoints with sample images
4. 🔧 Integrate with your mobile app via the REST API
5. 📡 Use WebSockets for real-time updates

---

## Production Deployment

### Docker (Coming Soon)

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "run.py"]
```

### Cloud Deployment

- **AWS**: Elastic Beanstalk or ECS
- **GCP**: Cloud Run or App Engine
- **Azure**: App Service

Add environment variables via your cloud provider's dashboard.

---

## Support

For issues or questions:
- 📧 Email: support@nove.ai
- 📝 GitHub Issues: Create an issue
- 📚 Documentation: See `API.md`

---

## License

Proprietary - Nove Inc. 2025
