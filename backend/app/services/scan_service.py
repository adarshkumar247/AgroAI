import os
import uuid
from datetime import datetime
from typing import List, Optional
from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session

from backend.app.models.scan import Scan
from backend.app.ai.predictor import predictor

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

class ScanService:
    @staticmethod
    def get_all_scans(db: Session, user_id: Optional[str] = None) -> List[Scan]:
        query = db.query(Scan)
        if user_id:
            query = query.filter(Scan.user_id == user_id)
        return query.order_by(Scan.created_at.desc()).all()

    @staticmethod
    def get_scan_by_id(db: Session, scan_id: str, user_id: Optional[str] = None) -> Optional[Scan]:
        query = db.query(Scan).filter(Scan.id == scan_id)
        if user_id:
            query = query.filter(Scan.user_id == user_id)
        return query.first()

    @staticmethod
    async def create_scan(
        db: Session,
        image_file: UploadFile,
        crop_hint: Optional[str] = None,
        symptoms: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> Scan:
        # Validate file format
        allowed_extensions = {".jpg", ".jpeg", ".png", ".webp", ".heic"}
        ext = os.path.splitext(image_file.filename or "")[1].lower()
        if not ext:
            ext = ".png"
        if ext not in allowed_extensions:
            raise HTTPException(status_code=400, detail=f"Unsupported file format '{ext}'. Allowed: {allowed_extensions}")

        # Generate unique scan ID
        count = db.query(Scan).count() + 1
        scan_id = f"scan_{count:03d}"

        # Save file safely
        filename = f"{scan_id}_{uuid.uuid4().hex[:8]}{ext}"
        saved_path = os.path.join(UPLOAD_DIR, filename)

        contents = await image_file.read()
        if len(contents) > 25 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="File too large. Maximum size is 25MB.")

        with open(saved_path, "wb") as f:
            f.write(contents)

        # Run AI prediction
        ai_result = predictor.predict(
            image_path=saved_path,
            crop_hint=crop_hint,
            symptoms=symptoms
        )

        # Persist to database with user_id
        db_scan = Scan(
            id=scan_id,
            user_id=user_id,
            image_path=f"/uploads/{filename}",
            crop_name=ai_result["crop"],
            possible_issue=ai_result["possible_issue"],
            confidence=ai_result["confidence"],
            severity=ai_result["severity"],
            stage=ai_result["stage"],
            pathogen=ai_result["pathogen"],
            spread_risk=ai_result["spread_risk"],
            canopy_loss=ai_result["canopy_loss"],
            immediate_action=ai_result["immediate_action"],
            created_at=datetime.utcnow()
        )
        db.add(db_scan)
        db.commit()
        db.refresh(db_scan)

        return db_scan
