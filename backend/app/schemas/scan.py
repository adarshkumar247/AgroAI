from typing import Optional, List
from pydantic import BaseModel

class HealthResponse(BaseModel):
    status: str = "ok"

class ScanResponse(BaseModel):
    scan_id: str
    crop: str
    possible_issue: str
    confidence: float
    severity: Optional[str] = "Moderate"
    stage: Optional[str] = "Stage 2 — Mild Spread"
    pathogen: Optional[str] = "Alternaria solani"
    spread_risk: Optional[str] = "Moderate"
    canopy_loss: Optional[str] = "< 4%"
    immediate_action: Optional[str] = "Prune affected lower leaves, switch to targeted drip irrigation, apply protective mulch."
    image_url: Optional[str] = None
    created_at: Optional[str] = None

    class Config:
        from_attributes = True

class ScanListResponse(BaseModel):
    total: int
    scans: List[ScanResponse]
