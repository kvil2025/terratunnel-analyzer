# ============================================================
# TerraTunnel Analyzer — Local Build Script (Windows)
# ============================================================
# Builds the frontend and copies it into the backend's static
# directory, then starts the unified server on port 8000.
#
# Usage:
#   .\build.ps1              → Build + start in DEMO mode
#   .\build.ps1 -Live        → Build + start in LIVE mode (needs API key in .env)
#   .\build.ps1 -BuildOnly   → Build only, don't start server
# ============================================================

param(
    [switch]$Live,
    [switch]$BuildOnly
)

$ErrorActionPreference = "Stop"
$ProjectRoot = $PSScriptRoot
$FrontendDir = Join-Path $ProjectRoot "frontend"
$BackendDir  = Join-Path $ProjectRoot "backend"
$StaticDir   = Join-Path $BackendDir "static"

Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  TerraTunnel Analyzer — Build System" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# ── Step 1: Install frontend dependencies ─────────────────────
Write-Host "[1/4] Checking frontend dependencies..." -ForegroundColor Yellow
Push-Location $FrontendDir
if (-not (Test-Path "node_modules")) {
    Write-Host "       Installing npm packages..." -ForegroundColor Gray
    npm install --silent 2>&1 | Out-Null
}
Pop-Location
Write-Host "       OK" -ForegroundColor Green

# ── Step 2: Build frontend ────────────────────────────────────
Write-Host "[2/4] Building frontend (Vite)..." -ForegroundColor Yellow
Push-Location $FrontendDir
npm run build 2>&1 | Out-Null
Pop-Location
Write-Host "       OK" -ForegroundColor Green

# ── Step 3: Copy build to backend/static ──────────────────────
Write-Host "[3/4] Copying build to backend/static..." -ForegroundColor Yellow
if (Test-Path $StaticDir) {
    Remove-Item -Recurse -Force $StaticDir
}
Copy-Item -Recurse (Join-Path $FrontendDir "dist") $StaticDir
Write-Host "       OK" -ForegroundColor Green

# ── Step 4: Install Python dependencies ───────────────────────
Write-Host "[4/4] Checking Python dependencies..." -ForegroundColor Yellow
Push-Location $BackendDir
pip install -q -r requirements.txt 2>&1 | Out-Null
Pop-Location
Write-Host "       OK" -ForegroundColor Green

Write-Host ""
Write-Host "Build complete!" -ForegroundColor Green
Write-Host ""

if ($BuildOnly) {
    Write-Host "Build-only mode. To start the server:" -ForegroundColor Gray
    Write-Host "  cd backend && python main.py" -ForegroundColor White
    exit 0
}

# ── Start server ──────────────────────────────────────────────
if ($Live) {
    Write-Host "Starting in LIVE mode (GLM-5.2)..." -ForegroundColor Magenta
    $env:MODE = "live"
} else {
    Write-Host "Starting in DEMO mode..." -ForegroundColor Yellow
    $env:MODE = "demo"
}

Write-Host "Server: http://localhost:8000" -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop." -ForegroundColor Gray
Write-Host ""

Push-Location $BackendDir
python main.py
Pop-Location
