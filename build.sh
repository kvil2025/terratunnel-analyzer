#!/usr/bin/env bash
# ============================================================
# TerraTunnel Analyzer — Build Script (Linux/Mac)
# ============================================================
# Builds the frontend and copies it into the backend's static
# directory, then starts the unified server on port 8000.
#
# Usage:
#   ./build.sh              → Build + start in DEMO mode
#   ./build.sh --live       → Build + start in LIVE mode
#   ./build.sh --build-only → Build only, don't start server
# ============================================================

set -e

PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
FRONTEND_DIR="$PROJECT_ROOT/frontend"
BACKEND_DIR="$PROJECT_ROOT/backend"
STATIC_DIR="$BACKEND_DIR/static"

LIVE=false
BUILD_ONLY=false

for arg in "$@"; do
  case $arg in
    --live) LIVE=true ;;
    --build-only) BUILD_ONLY=true ;;
  esac
done

echo ""
echo "================================================"
echo "  TerraTunnel Analyzer — Build System"
echo "================================================"
echo ""

# ── Step 1: Install frontend dependencies
echo "[1/4] Checking frontend dependencies..."
cd "$FRONTEND_DIR"
if [ ! -d "node_modules" ]; then
    echo "       Installing npm packages..."
    npm install --silent > /dev/null 2>&1
fi
echo "       OK"

# ── Step 2: Build frontend
echo "[2/4] Building frontend (Vite)..."
npm run build > /dev/null 2>&1
echo "       OK"

# ── Step 3: Copy build to backend/static
echo "[3/4] Copying build to backend/static..."
rm -rf "$STATIC_DIR"
cp -r "$FRONTEND_DIR/dist" "$STATIC_DIR"
echo "       OK"

# ── Step 4: Install Python dependencies
echo "[4/4] Checking Python dependencies..."
cd "$BACKEND_DIR"
pip install -q -r requirements.txt > /dev/null 2>&1
echo "       OK"

echo ""
echo "Build complete!"
echo ""

if [ "$BUILD_ONLY" = true ]; then
    echo "Build-only mode. To start the server:"
    echo "  cd backend && python main.py"
    exit 0
fi

# ── Start server
cd "$BACKEND_DIR"
if [ "$LIVE" = true ]; then
    echo "Starting in LIVE mode (GLM-5.2)..."
    export MODE=live
else
    echo "Starting in DEMO mode..."
    export MODE=demo
fi

echo "Server: http://localhost:${PORT:-8000}"
echo "Press Ctrl+C to stop."
echo ""

python main.py
