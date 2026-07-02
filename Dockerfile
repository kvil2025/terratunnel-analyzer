# ============================================================
# TerraTunnel Analyzer — Multi-Stage Dockerfile
# ============================================================
# Stage 1: Build the React frontend with Node
# Stage 2: Run the FastAPI backend with Python, serving static
# ============================================================

# ── Stage 1: Build Frontend ──────────────────────────────────
FROM node:20-alpine AS frontend-builder

WORKDIR /build
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm install --silent

COPY frontend/ ./
RUN npm run build


# ── Stage 2: Production Server ───────────────────────────────
FROM python:3.12-slim

WORKDIR /app

# Install Python dependencies
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source
COPY backend/ ./

# Copy frontend build output into backend/static
COPY --from=frontend-builder /build/dist ./static

# Environment defaults
ENV PORT=8000
ENV MODE=""
ENV ZHIPU_API_KEY=""
ENV ZHIPU_API_BASE="https://api.z.ai/api/paas/v4"
ENV GLM_MODEL="glm-5.2"

EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/health')" || exit 1

CMD ["python", "main.py"]
