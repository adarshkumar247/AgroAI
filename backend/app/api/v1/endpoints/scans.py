from typing import List, Optional
from fastapi import APIRouter, Depends, File, Form, UploadFile, HTTPException, Query
from sqlalchemy.orm import Session

from backend.app.database.session import get_db
from backend.app.schemas.scan import ScanResponse
from backend.app.services.scan_service import ScanService
from backend.app.core.security import get_optional_current_user
from backend.app.models.user import User

router = APIRouter()

@router.post("", response_model=ScanResponse, status_code=201)
async def create_scan(
    image: UploadFile = File(...),
    crop: Optional[str] = Form(None),
    symptoms: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    scan = await ScanService.create_scan(
        db=db,
        image_file=image,
        crop_hint=crop,
        symptoms=symptoms,
        user_id=current_user.id if current_user else None
    )
    return ScanResponse(
        scan_id=scan.id,
        crop=scan.crop_name,
        possible_issue=scan.possible_issue,
        confidence=scan.confidence,
        severity=scan.severity,
        stage=scan.stage,
        pathogen=scan.pathogen,
        spread_risk=scan.spread_risk,
        canopy_loss=scan.canopy_loss,
        immediate_action=scan.immediate_action,
        image_url=scan.image_path,
        created_at=scan.created_at.isoformat() if scan.created_at else None
    )

@router.get("", response_model=List[ScanResponse])
def list_scans(
    all_scans: bool = Query(False, alias="all"),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    target_user_id = None
    if current_user and not all_scans:
        target_user_id = current_user.id
    scans = ScanService.get_all_scans(db, user_id=target_user_id)
    return [
        ScanResponse(
            scan_id=s.id,
            crop=s.crop_name,
            possible_issue=s.possible_issue,
            confidence=s.confidence,
            severity=s.severity,
            stage=s.stage,
            pathogen=s.pathogen,
            spread_risk=s.spread_risk,
            canopy_loss=s.canopy_loss,
            immediate_action=s.immediate_action,
            image_url=s.image_path,
            created_at=s.created_at.isoformat() if s.created_at else None
        )
        for s in scans
    ]

@router.get("/{scan_id}", response_model=ScanResponse)
def get_scan(scan_id: str, db: Session = Depends(get_db)):
    scan = ScanService.get_scan_by_id(db, scan_id)
    if not scan:
        raise HTTPException(status_code=404, detail=f"Scan with ID '{scan_id}' not found.")
    return ScanResponse(
        scan_id=scan.id,
        crop=scan.crop_name,
        possible_issue=scan.possible_issue,
        confidence=scan.confidence,
        severity=scan.severity,
        stage=scan.stage,
        pathogen=scan.pathogen,
        spread_risk=scan.spread_risk,
        canopy_loss=scan.canopy_loss,
        immediate_action=scan.immediate_action,
        image_url=scan.image_path,
        created_at=scan.created_at.isoformat() if scan.created_at else None
    )
