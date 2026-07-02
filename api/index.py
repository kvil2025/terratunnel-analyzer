"""
TerraTunnel Analyzer — Vercel Serverless Entry Point
=====================================================
Wraps the FastAPI app for Vercel's Python serverless runtime.
Vercel auto-detects the `app` object as an ASGI application.
"""

import sys
import os
from pathlib import Path

# ── Add backend directory to Python path ──────────────────────
backend_dir = str(Path(__file__).resolve().parent.parent / "backend")
sys.path.insert(0, backend_dir)

# ── Load environment from backend/.env if present ─────────────
env_file = Path(__file__).resolve().parent.parent / "backend" / ".env"
if env_file.exists():
    from dotenv import load_dotenv
    load_dotenv(env_file)

# ── Import the FastAPI app ────────────────────────────────────
# This imports the full app with all API routes.
# Static file serving is auto-disabled (HAS_STATIC=False in serverless)
# because backend/static/ doesn't exist in the Vercel build.
from main import app  # noqa: F401, E402
