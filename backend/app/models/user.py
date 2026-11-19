from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from backend.app.database.base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(String(50), primary_key=True, index=True)
    full_name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    location = Column(String(150), default="Lucknow Farm, Uttar Pradesh")
    preferred_language = Column(String(50), default="Hindi (HI)")
    profile_photo_url = Column(String(255), nullable=True)
    farm_name = Column(String(150), nullable=True)
    main_crop = Column(String(100), nullable=True)
    farm_size = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    scans = relationship("Scan", back_populates="user", cascade="all, delete-orphan")
    sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "full_name": self.full_name,
            "email": self.email,
            "location": self.location,
            "preferred_language": self.preferred_language,
            "profile_photo_url": self.profile_photo_url,
            "farm_name": self.farm_name,
            "main_crop": self.main_crop,
            "farm_size": self.farm_size,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

class UserSession(Base):
    __tablename__ = "user_sessions"

    id = Column(String(50), primary_key=True, index=True)
    user_id = Column(String(50), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    token = Column(String(100), unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="sessions")
