import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from backend.app.api.v1.api import api_router
from backend.app.database.session import init_db

app = FastAPI(
    title="AgroAI Smart Agriculture API",
    description="Backend API for AgroAI Crop Diagnostic & Farm Management Assistant",
    version="1.0.0"
)

# Configure CORS for local development and frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Project root (contains index.html, js/ and assets/)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Ensure upload directory exists and mount static uploads
UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# Include API Router
app.include_router(api_router, prefix="/api/v1")

# Serve the static frontend from the same service (single-container Render deploy).
# Only the public frontend folders are mounted; source code, .env and the database
# remain private.
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
JS_DIR = os.path.join(BASE_DIR, "js")
INDEX_FILE = os.path.join(BASE_DIR, "index.html")

if os.path.isdir(ASSETS_DIR):
    app.mount("/assets", StaticFiles(directory=ASSETS_DIR), name="assets")
if os.path.isdir(JS_DIR):
    app.mount("/js", StaticFiles(directory=JS_DIR), name="js")

@app.on_event("startup")
def on_startup():
    init_db()

@app.get("/", include_in_schema=False)
def serve_frontend():
    if os.path.isfile(INDEX_FILE):
        return FileResponse(INDEX_FILE)
    return {
        "app": "AgroAI Smart Agriculture API",
        "status": "online",
        "docs_url": "/docs",
        "health_check": "/api/v1/health"
    }
