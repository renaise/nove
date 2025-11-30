# Novia Backend

AI-powered wedding dress virtual try-on backend.

## Stack

- **FastAPI** - Modern async web framework
- **Strawberry** - GraphQL with Python type hints
- **SQLAlchemy** - Async ORM with asyncpg
- **Temporal** - Workflow orchestration for job queuing
- **Google GenAI** - Nano Banana Pro for image generation
- **Cloudflare R2** - Image storage (S3-compatible)

## Setup

### Prerequisites

- Python 3.11+
- PostgreSQL 14+
- Temporal server (local or cloud)
- Google GenAI API key
- Cloudflare R2 bucket

### Installation

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # or `.venv\Scripts\activate` on Windows

# Install dependencies
pip install -e ".[dev]"

# Copy environment file
cp .env.example .env
# Edit .env with your credentials
```

### Database Setup

```bash
# Run migrations (creates tables)
# Tables are auto-created on first startup, or use Alembic:
alembic upgrade head
```

### Running

```bash
# Terminal 1: Start the API server
uvicorn src.main:app --reload --port 8000

# Terminal 2: Start the Temporal worker
python -m src.temporal.worker

# Terminal 3: Start Temporal server (if running locally)
temporal server start-dev
```

### Development

```bash
# Format code
ruff format .

# Lint
ruff check .

# Type check
mypy src

# Run tests
pytest
```

## API

### GraphQL Endpoint

`POST /graphql`

### Example Queries

```graphql
# List available dresses
query {
  dresses {
    id
    name
    imageUrl
    style
  }
}

# Create a try-on request
mutation {
  createTryOn(input: {
    personImageBase64: "..."
    dressId: "dress-uuid"
  }) {
    id
    status
    message
  }
}

# Check try-on status
query {
  tryOnRequest(id: "request-uuid") {
    id
    status
    resultImageUrl
    errorMessage
  }
}
```

### REST Endpoints

- `GET /health` - Health check
- `GET /docs` - OpenAPI documentation
- `GET /graphql` - GraphQL Playground

## Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Mobile    │────▶│   FastAPI   │────▶│  PostgreSQL │
│    App      │     │  (GraphQL)  │     │             │
└─────────────┘     └──────┬──────┘     └─────────────┘
                          │
                          ▼
                   ┌─────────────┐
                   │  Temporal   │
                   │   Server    │
                   └──────┬──────┘
                          │
                          ▼
                   ┌─────────────┐     ┌─────────────┐
                   │   Worker    │────▶│ Google GenAI│
                   │ (Activities)│     │(Nano Banana)│
                   └──────┬──────┘     └─────────────┘
                          │
                          ▼
                   ┌─────────────┐
                   │ Cloudflare  │
                   │     R2      │
                   └─────────────┘
```

## Workflow

1. User uploads photo via GraphQL mutation
2. Request is saved to DB with PENDING status
3. Temporal workflow is started
4. Worker executes activities:
   - Upload person image to R2
   - Fetch dress image URL
   - Call Nano Banana Pro API
   - Upload result to R2
   - Update DB with result
5. Mobile app polls for status or uses subscription
