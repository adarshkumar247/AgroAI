from fastapi import APIRouter
from backend.app.api.v1.endpoints import (
    health,
    scans,
    weather,
    assistant,
    irrigation,
    nutrients,
    crop_id,
    dashboard,
    auth
)

api_router = APIRouter()
api_router.include_router(health.router, tags=["Health"])
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(scans.router, prefix="/scans", tags=["Scans"])
api_router.include_router(weather.router, prefix="/weather", tags=["Weather"])
api_router.include_router(assistant.router, prefix="/assistant", tags=["AI Assistant"])
api_router.include_router(irrigation.router, prefix="/irrigation", tags=["Smart Irrigation"])
api_router.include_router(nutrients.router, prefix="/nutrients", tags=["Nutrients & Fertilizer"])
api_router.include_router(crop_id.router, prefix="/crop-id", tags=["Crop Identification"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard & Insights"])
