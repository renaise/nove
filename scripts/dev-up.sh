#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

echo "🚀 Starting Novia development environment..."

# Check if Python venv exists
if [ ! -d "$ROOT_DIR/backend/.venv" ]; then
    echo "📦 Setting up Python environment..."
    cd "$ROOT_DIR/backend"
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -e ".[dev]"
    cd "$ROOT_DIR"
fi

# Check if Temporal CLI is installed
if ! command -v temporal &> /dev/null; then
    echo "⚠️  Temporal CLI not found. Install with: brew install temporal"
    exit 1
fi

# Check if PM2 is installed
if ! command -v pm2 &> /dev/null; then
    echo "⚠️  PM2 not found. Install with: npm install -g pm2"
    exit 1
fi

echo "📡 Starting services with PM2..."
cd "$ROOT_DIR"
pm2 start ecosystem.config.cjs

echo ""
echo "✅ All services started!"
echo ""
echo "   📱 Lynx:     http://localhost:3000"
echo "   🌐 API:      http://localhost:8000"
echo "   📊 GraphQL:  http://localhost:8000/graphql"
echo "   🕐 Temporal: http://localhost:8233"
echo ""
echo "Commands:"
echo "   npm run dev:logs    - View logs"
echo "   npm run dev:status  - Check status"
echo "   npm run dev:down    - Stop all services"
echo ""
