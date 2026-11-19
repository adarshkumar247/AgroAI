from typing import Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.database.session import get_db
from backend.app.services.dashboard_service import DashboardService
from backend.app.core.security import get_optional_current_user
from backend.app.models.user import User

router = APIRouter()

@router.get("/summary")
def get_dashboard_summary(
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    """Retrieve aggregated live farm telemetry, SQLite scan metrics, and Open-Meteo weather."""
    return DashboardService.get_summary(db=db, user=current_user)
