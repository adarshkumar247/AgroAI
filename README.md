# AgroAI — Smart Agriculture Assistant

AgroAI is an AI-powered smart agriculture assistant designed for precision farming, disease diagnosis, and agronomic management.

This project integrates the **Google Stitch UI** (Material 3 Botanical Functionalism theme) as the visual source of truth with a modular **Python + FastAPI + SQLite** backend and an AI predictor engine.

---

## Architecture Overview

```text
Stitch HTML/JS Frontend (Port 8080)
           │
           │ HTTP Fetch (POST /api/v1/scans)
           ▼
FastAPI Python Backend (Port 8000)
           │
     ┌─────┴─────────────────────┐
     ▼                           ▼
SQLite Database (agroai.db)    CropDiseasePredictor (Mock AI)
(History & Telemetry)          (backend/app/ai/predictor.py)
```

---

## Project Structure

```text
c:\agrofield\
├── index.html                           # Root application entry point (Router & Responsive Shell)
├── serve.ps1                            # Zero-dependency local web server
├── start-frontend.ps1                   # Frontend quick launcher
├── start-backend.ps1                    # FastAPI backend quick launcher
├── assets\                              # Localized Stitch image assets
│   ├── agroai-logo.png                  # AgroAI Logo
│   ├── farmer-avatar.png                # Farmer profile (Ramesh Patel)
│   ├── tomato-leaf-sample.png           # Diagnosed tomato leaf
│   └── paddy-rice-sample.png            # Healthy paddy rice stalks
├── js\
│   ├── app.js                           # Core app orchestrator, hash router, and drawer toggle
│   └── modules\                         # Modular views for all 10 AgroAI modules
│       ├── dashboard.js                 # AgroAI Main Dashboard
│       ├── scanner.js                   # Crop Scanner (file upload & API call)
│       ├── report.js                    # Crop Health Analysis Report
│       ├── crop-id.js                   # Crop Species Identification
│       ├── nutrients.js                 # NPK Soil Nutrition & Fertilizer Guidance
│       ├── irrigation.js                # Telemetry Smart Drip Irrigation
│       ├── weather.js                   # Micro-Climate Radar & Spray Advisories
│       ├── assistant.js                 # AgroAI Agronomic Copilot Chat
│       ├── history.js                   # Scan History (connected to SQLite)
│       ├── insights.js                  # Field Acreage & Yield Projections
│       └── settings.js                  # Settings & Profile
├── backend\
│   ├── requirements.txt                 # FastAPI, uvicorn, pydantic, sqlalchemy, multipart
│   ├── .env.example                     # Environment configuration
│   ├── agroai.db                        # SQLite database file
│   ├── uploads\                         # Uploaded leaf scans repository
│   └── app\
│       ├── main.py                      # FastAPI app entry point with CORS
│       ├── api\
│       │   └── v1\
│       │       ├── api.py               # V1 Router
│       │       └── endpoints\
│       │           ├── health.py        # GET /api/v1/health
│       │           └── scans.py         # POST /api/v1/scans, GET /api/v1/scans, GET /api/v1/scans/{id}
│       ├── services\
│       │   └── scan_service.py          # Scan orchestration & file validation
│       ├── models\
│       │   └── scan.py                  # SQLAlchemy Scan model
│       ├── schemas\
│       │   └── scan.py                  # Pydantic schemas
│       ├── database\
│       │   ├── session.py               # SQLite session factory
│       │   └── base.py                  # Declarative base
│       └── ai\
│           └── predictor.py             # Modular CropDiseasePredictor (swappable for PyTorch/TF)
└── stitch_agroai_smart_agriculture_assistant\   # Pristine Google Stitch source of truth
```

---

## Quick Start Guide

### ⚡ One-Click Startup (Frontend + Backend)

Simply run or double-click `start.bat`:

```cmd
start.bat
```

This automatically launches both the FastAPI backend and Frontend server in dedicated terminal windows and opens your browser.

---

### 1. Start the Python FastAPI Backend

Open a PowerShell terminal in `c:\agrofield`:

```powershell
.\start-backend.ps1
```

Or manually:

```powershell
.\backend\.venv\Scripts\uvicorn.exe backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```

* Backend URL: [http://127.0.0.1:8000](http://127.0.0.1:8000)
* Interactive API Documentation (Swagger): [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
* Health Check: [http://127.0.0.1:8000/api/v1/health](http://127.0.0.1:8000/api/v1/health)

---

### 2. Start the Frontend Server

Open a second PowerShell terminal in `c:\agrofield`:

```powershell
.\start-frontend.ps1
```

Or manually:

```powershell
powershell -ExecutionPolicy Bypass -File ".\serve.ps1" -Port 8080
```

* Frontend Application: [http://localhost:8080/](http://localhost:8080/)

---

## API Reference

### Health Check
* **GET** `/api/v1/health`
* Response: `{"status": "ok"}`

### Create Crop Scan
* **POST** `/api/v1/scans`
* Multipart Form Data:
  * `image`: Binary file (`.png`, `.jpg`, `.jpeg`, `.webp`, `.heic` up to 25MB)
  * `crop`: (Optional) String, e.g. `"Tomato"`, `"Paddy Rice"`, `"Wheat"`
  * `symptoms`: (Optional) String, e.g. `"Brown concentric spots"`
* Response:
  ```json
  {
    "scan_id": "scan_001",
    "crop": "Tomato (Solanum lycopersicum)",
    "possible_issue": "Early Blight",
    "confidence": 0.91,
    "severity": "Attention Needed",
    "stage": "Stage 2 — Mild Spread",
    "pathogen": "Alternaria solani",
    "spread_risk": "Moderate",
    "canopy_loss": "< 4%",
    "immediate_action": "Prune affected lower leaves, switch to targeted drip irrigation, apply protective mulch.",
    "image_url": "/uploads/scan_001_abc123.png",
    "created_at": "2026-09-18T16:35:02.513369"
  }
  ```

### List All Scans
* **GET** `/api/v1/scans`
* Response: Array of `ScanResponse` objects ordered by newest first.

### Get Scan by ID
* **GET** `/api/v1/scans/{scan_id}`
* Response: Specific `ScanResponse` object.

---

## How to Replace the Mock AI with Real Model Weights

The inference logic is fully encapsulated in `backend/app/ai/predictor.py`.
FastAPI route files do **not** contain machine learning logic.

To integrate PyTorch, TensorFlow, or ONNX:
1. Install your framework in the virtual environment:
   ```powershell
   .\backend\.venv\Scripts\pip.exe install torch torchvision
   ```
2. In `backend/app/ai/predictor.py`, load your `.pt`, `.onnx`, or `.h5` file inside `__init__()`.
3. In `predict()`, preprocess the image from `image_path`, run model inference, and return the dictionary matching the schema.
4. No changes to the frontend or API endpoints will be necessary.

---

## Deployment

Single-service deployment: **Render runs FastAPI and also serves the static
frontend** (`index.html`, `js/`, `assets/`) from the same URL. No separate
frontend host is needed.

The repository includes `Dockerfile`, `.dockerignore` and `render.yaml`.
`js/config.js` automatically uses the same origin in production, so no API URL
needs to be configured.

See **[DEPLOYMENT.md](DEPLOYMENT.md)** for the complete step-by-step guide.
