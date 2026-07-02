"""
TerraTunnel Analyzer — FastAPI Backend (Production-Ready)
==========================================================
Exposes the multi-agent analysis pipeline via a REST API.
In production, also serves the compiled React frontend as static files.

Endpoints:
  POST /api/analyze  — Run multi-agent analysis on spec text
  POST /api/upload   — Upload PDF/DOCX/TXT and run analysis
  GET  /api/health   — Health check (includes mode detection)
  GET  /api/demo     — Run with sample tunnel specification
  *    /*             — Serve React SPA (production only)
"""

from __future__ import annotations

import io
import os
from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, File, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

load_dotenv()

from agents.orchestrator import Orchestrator  # noqa: E402
from agents.core import is_demo_mode  # noqa: E402


# ---------------------------------------------------------------------------
# Path configuration
# ---------------------------------------------------------------------------

# Static files directory: backend/static (populated by build script)
STATIC_DIR = Path(__file__).parent / "static"
HAS_STATIC = STATIC_DIR.exists() and (STATIC_DIR / "index.html").exists()


# ---------------------------------------------------------------------------
# Lifespan (warm-up on startup)
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    mode = "DEMO" if is_demo_mode() else "LIVE (GLM-5.2)"
    serving = "API + Frontend (unified)" if HAS_STATIC else "API only (dev mode)"
    port = os.getenv("PORT", "8000")
    print(f"[TerraTunnel] Mode: {mode}")
    print(f"[TerraTunnel] Serving: {serving}")
    print(f"[TerraTunnel] URL: http://localhost:{port}")
    yield
    print("[TerraTunnel] Shutting down")


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

app = FastAPI(
    title="TerraTunnel Analyzer API",
    description="Multi-agent tunnel contract & specification analyzer powered by GLM-5.2",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------

class AnalyzeRequest(BaseModel):
    spec_text: str


class HealthResponse(BaseModel):
    status: str
    mode: str
    version: str


# ---------------------------------------------------------------------------
# Sample specification for the demo endpoint
# ---------------------------------------------------------------------------

SAMPLE_SPEC = """\
PROYECTO: TÚNEL VIAL LOS ANDES — TRAMO KM 0+000 A KM 4+200
LONGITUD TOTAL: 4.200 metros
SECCIÓN: Herradura modificada, 12.5m de ancho x 9.8m de alto (área ~95 m²)
MÉTODO DE EXCAVACIÓN: Convencional — Perforación y Voladura (Drill & Blast)

=== CONDICIONES GEOLÓGICAS (Extracto del GBR) ===

Tramo 1 (Km 0+000 - Km 1+500): Granito masivo a ligeramente fracturado.
  RMR: 55-70 (Clase II-III). Q-system: 8-15.
  Sostenimiento Tipo I: Pernos puntuales de 3m, shotcrete de 50mm donde necesario.

Tramo 2 (Km 1+500 - Km 2+400): Granodiorita moderada a altamente fracturada.
  Roca de calidad regular a pobre. Q-system: Q=0.4.
  RMR: 41-60 (Clase III — roca regular).
  Sostenimiento Tipo II: Pernos sistemáticos de 3m a 2.0m de espaciamiento.

Tramo 3 (Km 2+400 - Km 3+100): Zona de falla con roca muy fracturada y arcillas.
  RMR: 30-35 (Clase IV — roca pobre).
  Presencia de arcillas montmorilloníticas en relleno de fallas.
  Cobertura: 120-180m. Nivel freático 40m sobre clave del túnel.
  Presión de agua estimada: hasta 5 bar en zona de falla (Km 2+800-2+950).
  Sostenimiento Tipo III: Pernos de anclaje puntuales sin shotcrete.

Tramo 4 (Km 3+100 - Km 4+200): Gneis de buena calidad.
  RMR: 60-75 (Clase II). Q-system: 10-25.
  Sostenimiento Tipo I.

Avance de excavación propuesto: 3-4m para todos los tramos.

=== CLÁUSULAS CONTRACTUALES (Extracto) ===

Cláusula 4.12 — Condiciones del Subsuelo:
"El Contratista acepta y asume todos los riesgos derivados de las condiciones
del subsuelo encontradas durante la excavación del túnel, incluyendo pero no
limitado a: variaciones en la clasificación de roca, presencia de agua
subterránea, zonas de falla, y cualquier otra condición geológica adversa.
El Contratista declara haber realizado su propia investigación del sitio."

Cláusula 20.1 — Notificación de Reclamos:
"Todo reclamo deberá ser notificado por escrito dentro de los 7 días
calendario siguientes a la ocurrencia del evento que da origen al reclamo.
La falta de notificación oportuna constituirá una renuncia irrevocable
al derecho de reclamo."

Sección 5.1 — Control de Aguas:
"El Contratista implementará las medidas necesarias para el control de
aguas subterráneas durante la excavación."

Sección 7.2 — Monitoreo Geotécnico:
"Se instalarán puntos de convergencia cada 25m a lo largo del túnel."

Tabla de Cantidades — Ítem 4.3 — Sostenimiento:
"Sostenimiento completo del túnel: precio global por metro lineal
de túnel excavado. Incluye todos los tipos de sostenimiento."

Cláusula 20 — Resolución de Disputas:
"Toda disputa será resuelta mediante arbitraje ad-hoc bajo las
reglas de la cámara de comercio local."
"""


# ---------------------------------------------------------------------------
# API Endpoints
# ---------------------------------------------------------------------------

@app.get("/api/health", response_model=HealthResponse)
async def health():
    return HealthResponse(
        status="ok",
        mode="demo" if is_demo_mode() else "live",
        version="1.0.0",
    )


@app.post("/api/analyze")
async def analyze(req: AnalyzeRequest):
    """Run the full multi-agent analysis pipeline."""
    orchestrator = Orchestrator()
    report = orchestrator.analyze(req.spec_text)
    return report.to_dict()


@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload a PDF, DOCX, or TXT file and run multi-agent analysis."""
    if not file.filename:
        return JSONResponse({"error": "No file provided"}, status_code=400)

    ext = Path(file.filename).suffix.lower()
    raw_bytes = await file.read()

    try:
        if ext == ".pdf":
            text = _extract_pdf(raw_bytes)
        elif ext in (".docx", ".doc"):
            text = _extract_docx(raw_bytes)
        elif ext == ".txt":
            text = raw_bytes.decode("utf-8", errors="replace")
        else:
            return JSONResponse(
                {"error": f"Formato no soportado: {ext}. Use PDF, DOCX o TXT."},
                status_code=400,
            )
    except Exception as exc:
        return JSONResponse(
            {"error": f"Error al leer el archivo: {exc}"},
            status_code=422,
        )

    if len(text.strip()) < 20:
        return JSONResponse(
            {"error": "El archivo no contiene suficiente texto para analizar."},
            status_code=422,
        )

    orchestrator = Orchestrator()
    report = orchestrator.analyze(text)
    return {
        "source_file": file.filename,
        "extracted_chars": len(text),
        "extracted_text_preview": text[:500],
        **report.to_dict(),
    }


# ---------------------------------------------------------------------------
# File parsing helpers
# ---------------------------------------------------------------------------

def _extract_pdf(raw_bytes: bytes) -> str:
    """Extract text from a PDF using PyMuPDF (fitz)."""
    import fitz  # PyMuPDF

    pages = []
    with fitz.open(stream=raw_bytes, filetype="pdf") as doc:
        for i, page in enumerate(doc):
            text = page.get_text()
            if text.strip():
                pages.append(f"[PÁGINA {i + 1}]\n{text}")
    return "\n\n".join(pages)


def _extract_docx(raw_bytes: bytes) -> str:
    """Extract text from a DOCX using python-docx."""
    from docx import Document

    doc = Document(io.BytesIO(raw_bytes))
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    return "\n\n".join(paragraphs)


@app.get("/api/demo")
async def demo():
    """Run analysis with the built-in sample tunnel specification."""
    orchestrator = Orchestrator()
    report = orchestrator.analyze(SAMPLE_SPEC)
    return {
        "sample_spec": SAMPLE_SPEC,
        **report.to_dict(),
    }


# ---------------------------------------------------------------------------
# Static file serving (production — after API routes)
# ---------------------------------------------------------------------------

if HAS_STATIC:
    # Mount static assets (JS, CSS, images) — but NOT at root to avoid
    # catching API routes. We mount at /assets which is where Vite outputs.
    assets_dir = STATIC_DIR / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")

    # Serve other static files (favicon, icons, etc.)
    @app.get("/favicon.svg")
    async def favicon():
        fav = STATIC_DIR / "favicon.svg"
        if fav.exists():
            return FileResponse(str(fav), media_type="image/svg+xml")
        return HTMLResponse("", status_code=404)

    @app.get("/icons.svg")
    async def icons():
        ico = STATIC_DIR / "icons.svg"
        if ico.exists():
            return FileResponse(str(ico), media_type="image/svg+xml")
        return HTMLResponse("", status_code=404)

    # SPA fallback: any non-API, non-asset route → index.html
    @app.get("/{full_path:path}")
    async def serve_spa(request: Request, full_path: str):
        # If it's an API route that wasn't matched, return 404
        if full_path.startswith("api/"):
            return HTMLResponse('{"error": "Not found"}', status_code=404)
        return FileResponse(str(STATIC_DIR / "index.html"), media_type="text/html")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "8000"))
    is_dev = os.getenv("ENV", "production") == "development"

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=is_dev,
    )
