# Nove Stitch Engine API Documentation

## Overview

The Stitch Engine is the AI-orchestrated backend for Nove's virtual try-on system. It uses **Claude Opus 4.5** for intelligent image analysis and orchestration.

## Base URL

```
http://localhost:8000
```

## Authentication

*(Future implementation - OAuth 2.0 for boutiques, JWT for brides)*

---

## Endpoints

### Health & Status

#### `GET /`

Get API status and version information.

**Response:**
```json
{
  "service": "Nove Stitch Engine",
  "version": "0.1.0",
  "status": "operational",
  "ai_model": "claude-opus-4-5-20251101",
  "timestamp": "2025-01-15T12:00:00.000000"
}
```

#### `GET /health`

Health check endpoint for monitoring.

**Response:**
```json
{
  "status": "healthy",
  "uploads_dir": "./uploads",
  "temp_dir": "./temp"
}
```

---

### Bride Silhouette Pipeline

#### `POST /bride/upload`

Upload a bride silhouette image.

**Request:**
- `Content-Type: multipart/form-data`
- `file`: Image file (JPEG, PNG, WEBP)

**Response:**
```json
{
  "image_id": "20250115120000_a1b2c3d4e5f6g7h8",
  "filename": "bride_silhouette.jpg",
  "message": "Image uploaded successfully. Use /bride/process to validate."
}
```

#### `POST /bride/process`

Process and validate bride silhouette with AI.

**Request:**
```json
{
  "image_id": "20250115120000_a1b2c3d4e5f6g7h8",
  "privacy_mode": true
}
```

**Response:**
```json
{
  "silhouette_id": "20250115120000_a1b2c3d4e5f6g7h8",
  "status": "completed",
  "quality": {
    "is_valid": true,
    "score": 0.92,
    "issues": [],
    "recommendations": ["Excellent A-pose detected"]
  },
  "processed_at": "2025-01-15T12:00:05.000000",
  "message": "Silhouette processed successfully (quality score: 0.92)"
}
```

**AI Validation Checks:**
- ✅ A-pose detection
- ✅ Image clarity and lighting
- ✅ Privacy compliance (face obscured)
- ✅ Body segmentation feasibility

---

### Boutique Garment Pipeline

#### `POST /boutique/upload`

Upload a boutique garment image.

**Request:**
- `Content-Type: multipart/form-data`
- `file`: Image file (JPEG, PNG, WEBP)

**Response:**
```json
{
  "image_id": "20250115120100_x9y8z7w6v5u4t3s2",
  "filename": "dress_001.jpg",
  "message": "Image uploaded successfully. Use /boutique/process to validate."
}
```

#### `POST /boutique/process`

Process and validate garment image with AI.

**Request:**
```json
{
  "image_id": "20250115120100_x9y8z7w6v5u4t3s2",
  "garment_name": "Lace A-Line Gown",
  "boutique_id": "boutique_001"
}
```

**Response:**
```json
{
  "garment_id": "boutique_001_20250115120100_x9y8z7w6v5u4t3s2",
  "status": "completed",
  "quality": {
    "is_valid": true,
    "score": 0.88,
    "issues": [],
    "recommendations": ["Good background contrast", "All details visible"]
  },
  "processed_at": "2025-01-15T12:01:05.000000",
  "message": "Garment 'Lace A-Line Gown' processed successfully (quality score: 0.88)"
}
```

**AI Validation Checks:**
- ✅ Background separation (white dress vs white wall)
- ✅ Garment completeness
- ✅ Lighting quality
- ✅ Fabric detail visibility

---

### Virtual Try-On Pipeline

#### `POST /tryon/process`

Generate virtual try-on render.

**Request:**
```json
{
  "silhouette_id": "20250115120000_a1b2c3d4e5f6g7h8",
  "garment_id": "boutique_001_20250115120100_x9y8z7w6v5u4t3s2",
  "render_quality": "standard"
}
```

**Response:**
```json
{
  "tryon_id": "20250115120000_a1b2c3d4e5f6g7h8_boutique_001_20250115120100_x9y8z7w6v5u4t3s2_1705320120",
  "status": "completed",
  "render_url": "/renders/20250115120000_a1b2c3d4e5f6g7h8_boutique_001_20250115120100_x9y8z7w6v5u4t3s2_1705320120.png",
  "processing_time_ms": 3450,
  "created_at": "2025-01-15T12:02:00.000000",
  "message": "Try-on completed (confidence: 0.85). Excellent size compatibility. Classic A-line style suits body type."
}
```

**Render Quality Options:**
- `fast`: Quick preview (512px)
- `standard`: Default quality (1024px) - **Default**
- `high`: Maximum quality (2048px)

**AI Orchestration:**
- 🧠 Size compatibility analysis
- 🧠 Style matching insights
- 🧠 Warping parameter optimization
- 🧠 Quality prediction

---

### WebSocket API

#### `WS /ws`

Real-time updates for processing status.

**Connect:**
```javascript
const ws = new WebSocket('ws://localhost:8000/ws');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Update:', data);
};
```

**Message Types:**

1. **Bride Processing**
```json
{
  "type": "bride_processing",
  "silhouette_id": "...",
  "status": "completed",
  "message": "Silhouette processed successfully"
}
```

2. **Garment Processing**
```json
{
  "type": "garment_processing",
  "garment_id": "...",
  "status": "completed",
  "message": "Garment processed successfully"
}
```

3. **Try-On Updates**
```json
{
  "type": "tryon_started",
  "silhouette_id": "...",
  "garment_id": "...",
  "status": "processing"
}
```

```json
{
  "type": "tryon_completed",
  "tryon_id": "...",
  "status": "completed",
  "render_url": "/renders/...",
  "processing_time_ms": 3450,
  "message": "Try-on completed successfully"
}
```

---

## Status Codes

- `200 OK` - Request successful
- `400 Bad Request` - Invalid input
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error

---

## Error Response Format

```json
{
  "error": "Error type",
  "detail": "Detailed error message",
  "timestamp": "2025-01-15T12:00:00.000000"
}
```

---

## Rate Limiting

*(Future implementation - 100 requests/minute per API key)*

---

## Example Usage

### Full Flow: Bride Try-On Experience

```bash
# 1. Upload bride silhouette
curl -X POST http://localhost:8000/bride/upload \
  -F "file=@bride.jpg"

# Response: { "image_id": "abc123..." }

# 2. Process silhouette with AI validation
curl -X POST http://localhost:8000/bride/process \
  -H "Content-Type: application/json" \
  -d '{"image_id": "abc123", "privacy_mode": true}'

# Response: { "silhouette_id": "abc123", "status": "completed", ... }

# 3. Upload boutique garment
curl -X POST http://localhost:8000/boutique/upload \
  -F "file=@dress.jpg"

# Response: { "image_id": "xyz789..." }

# 4. Process garment with AI validation
curl -X POST http://localhost:8000/boutique/process \
  -H "Content-Type: application/json" \
  -d '{
    "image_id": "xyz789",
    "garment_name": "Lace A-Line",
    "boutique_id": "boutique_001"
  }'

# Response: { "garment_id": "boutique_001_xyz789", "status": "completed", ... }

# 5. Generate virtual try-on
curl -X POST http://localhost:8000/tryon/process \
  -H "Content-Type: application/json" \
  -d '{
    "silhouette_id": "abc123",
    "garment_id": "boutique_001_xyz789",
    "render_quality": "standard"
  }'

# Response: { "tryon_id": "...", "render_url": "/renders/...", ... }

# 6. Access the render
curl http://localhost:8000/renders/[tryon_id].png > result.png
```

---

## AI Model Details

**Model:** Claude Opus 4.5 (`claude-opus-4-5-20251101`)

**Use Cases:**
1. **Image Quality Validation** - Analyzes uploaded images for technical quality
2. **Pose Detection** - Validates bride A-pose for accurate fitting
3. **Background Analysis** - Solves the "white dress on white wall" problem
4. **Orchestration** - Intelligently coordinates the try-on pipeline
5. **Style Matching** - Provides insights on garment-body compatibility

---

## Production Considerations

### Current Prototype Limitations

- ✅ Full Opus 4.5 AI orchestration
- ⚠️ Placeholder rendering (production would use ANNY warping)
- ⚠️ No SAM 3 segmentation yet (coming soon)
- ⚠️ No authentication (add before production)
- ⚠️ No database (using file system)

### Next Steps

1. Integrate SAM 3 for real segmentation
2. Integrate ANNY for fabric warping
3. Add PostgreSQL database
4. Implement authentication
5. Add CDN for render delivery
6. Set up monitoring and logging
