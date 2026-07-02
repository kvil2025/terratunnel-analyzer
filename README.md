# ⛏️ TerraTunnel Analyzer

**Multi-Agent AI Platform for Tunnel Construction Contract & Specification Analysis**

TerraTunnel Analyzer uses three specialized AI agents powered by GLM-5.2 to automatically review tunnel construction specifications and contracts, identifying geotechnical inconsistencies, contractual risks, and dangerous cross-domain conflicts.

![License](https://img.shields.io/badge/license-MIT-blue)
![Python](https://img.shields.io/badge/python-3.12+-green)
![Node](https://img.shields.io/badge/node-20+-green)
![Docker](https://img.shields.io/badge/docker-ready-blue)

---

## 🔍 What It Does

| Agent | Role | Standards |
|-------|------|-----------|
| **⛏️ GeoTech-Analyst** | Reviews rock classification, support systems, groundwater | Bieniawski RMR (1989), Barton Q-System, ITA Guidelines |
| **📜 Contract-Risk-Analyst** | Evaluates risk allocation, GBR compliance, dispute clauses | FIDIC Emerald Book (2019), ASCE MOP 154 |
| **🔗 Tunnel-Director** | Cross-domain synthesis, risk matrix, executive summary | Combined analysis |

### Key Outputs
- 📊 Interactive 5×5 Risk Matrix (Likelihood × Consequence)
- ⚖️ Support Comparison Table (Contract vs. International Standards)
- 📋 Executive Summary with prioritized recommendations
- 📥 Downloadable reports (JSON + printable HTML)

---

## 🚀 Quick Start

### Option 1: Local (Windows)
```powershell
git clone https://github.com/YOUR_USER/terratunnel-analyzer.git
cd terratunnel-analyzer
.\build.ps1
# → Opens at http://localhost:8000
```

### Option 2: Docker
```bash
docker compose up --build
# → Opens at http://localhost:8000
```

### Option 3: Railway (Cloud)
[![Deploy on Railway](https://railway.com/button.svg)](https://railway.app/template)

1. Fork this repo
2. Connect to [railway.app](https://railway.app)
3. Railway auto-detects the `Dockerfile` and deploys
4. Get your HTTPS URL: `https://terratunnel-xxxx.up.railway.app`

---

## 🔧 Configuration

Copy `backend/.env.example` to `backend/.env` and configure:

```env
# Leave as placeholder for DEMO mode (mock responses)
# Set a real Z.ai key for LIVE mode (GLM-5.2 analysis)
ZHIPU_API_KEY=your_api_key_here

# API endpoint
ZHIPU_API_BASE=https://api.z.ai/api/paas/v4

# Model
GLM_MODEL=glm-5.2
```

**Mode auto-detection**: The system automatically runs in DEMO mode if no valid API key is present, and switches to LIVE mode when a real key is configured.

---

## 📁 Project Structure

```
├── Dockerfile              # Multi-stage build (Node + Python)
├── docker-compose.yml      # One-command deployment
├── railway.toml            # Railway cloud config
├── build.ps1 / build.sh    # Local build scripts
├── backend/
│   ├── main.py             # FastAPI server (API + static files)
│   ├── agents/
│   │   ├── core.py         # Base Agent class + GLM-5.2 client
│   │   ├── geotech_agent.py    # Geotechnical analysis agent
│   │   ├── contract_agent.py   # Contractual risk agent
│   │   └── orchestrator.py     # Multi-agent orchestration
│   └── requirements.txt
└── frontend/
    ├── src/
    │   ├── App.jsx
    │   ├── index.css           # Premium glassmorphic design system
    │   └── components/
    │       ├── Header.jsx
    │       ├── SpecInput.jsx
    │       ├── AgentConsole.jsx
    │       ├── Dashboard.jsx
    │       ├── RiskGauge.jsx
    │       ├── RiskMatrix.jsx
    │       └── SupportComparison.jsx
    └── package.json
```

---

## 🔌 API Documentation

When running, Swagger docs are available at `/api/docs`.

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Health check + mode detection |
| `/api/analyze` | POST | Run multi-agent analysis on spec text |
| `/api/demo` | GET | Run analysis with sample tunnel specification |
| `/api/docs` | GET | Interactive API documentation (Swagger) |

---

## 📜 License

MIT License — See [LICENSE](LICENSE) for details.

---

## 👨‍💻 Author

Built with expertise in tunnel engineering and construction contract law, powered by GLM-5.2 multi-agent AI.
