from datetime import datetime
from sqlalchemy import Column, String, Float, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.database.base import Base

class Scan(Base):
    __tablename__ = "scans"

    id = Column(String(50), primary_key=True, index=True)
    user_id = Column(String(50), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    image_path = Column(String(255), nullable=False)
    crop_name = Column(String(100), nullable=False)
    possible_issue = Column(String(150), nullable=False)
    confidence = Column(Float, nullable=False)
    severity = Column(String(50), default="Moderate")
    stage = Column(String(50), default="Stage 2 — Mild Spread")
    pathogen = Column(String(150), nullable=True)
    spread_risk = Column(String(50), default="Moderate")
    canopy_loss = Column(String(50), default="< 5%")
    immediate_action = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("backend.app.models.user.User", back_populates="scans")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "image_path": self.image_path,
            "crop_name": self.crop_name,
            "possible_issue": self.possible_issue,
            "confidence": self.confidence,
            "severity": self.severity,
            "stage": self.stage,
            "pathogen": self.pathogen,
            "spread_risk": self.spread_risk,
            "canopy_loss": self.canopy_loss,
            "immediate_action": self.immediate_action,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
