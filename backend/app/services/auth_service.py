import uuid
from datetime import datetime, timedelta
from typing import Optional, Tuple
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from backend.app.models.user import User, UserSession
from backend.app.core.security import hash_password, verify_password, generate_session_token
from backend.app.schemas.auth import UserRegisterRequest, ProfileUpdateRequest

SESSION_EXPIRY_DAYS = 30

class AuthService:
    @staticmethod
    def register_user(db: Session, req: UserRegisterRequest) -> Tuple[User, str]:
        # Validate password match if confirm_password provided
        if req.confirm_password and req.password != req.confirm_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Passwords do not match."
            )

        # Check existing user
        clean_email = req.email.strip().lower()
        existing = db.query(User).filter(User.email == clean_email).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="An account with this email address already exists."
            )

        # Create user
        user_id = f"usr_{uuid.uuid4().hex[:12]}"
        new_user = User(
            id=user_id,
            full_name=req.full_name.strip(),
            email=clean_email,
            password_hash=hash_password(req.password),
            location=req.location.strip() if req.location else "Lucknow Farm, Uttar Pradesh",
            preferred_language=req.preferred_language or "English (EN)",
            created_at=datetime.utcnow()
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        # Create session
        token = AuthService._create_session(db, new_user.id)
        return new_user, token

    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> Tuple[User, str]:
        clean_email = email.strip().lower()
        user = db.query(User).filter(User.email == clean_email).first()
        if not user or not verify_password(password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password.",
                headers={"WWW-Authenticate": "Bearer"}
            )

        token = AuthService._create_session(db, user.id)
        return user, token

    @staticmethod
    def _create_session(db: Session, user_id: str) -> str:
        token = generate_session_token()
        session = UserSession(
            id=f"sess_{uuid.uuid4().hex[:12]}",
            user_id=user_id,
            token=token,
            created_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(days=SESSION_EXPIRY_DAYS)
        )
        db.add(session)
        db.commit()
        return token

    @staticmethod
    def get_user_by_token(db: Session, token: str) -> Optional[User]:
        if not token:
            return None
        session = db.query(UserSession).filter(UserSession.token == token).first()
        if not session:
            return None
        if session.expires_at and session.expires_at < datetime.utcnow():
            db.delete(session)
            db.commit()
            return None
        return session.user

    @staticmethod
    def logout_user(db: Session, token: str) -> bool:
        if not token:
            return False
        session = db.query(UserSession).filter(UserSession.token == token).first()
        if session:
            db.delete(session)
            db.commit()
            return True
        return False

    @staticmethod
    def update_profile(db: Session, user: User, req: ProfileUpdateRequest) -> User:
        if req.full_name is not None:
            user.full_name = req.full_name.strip()
        if req.location is not None:
            user.location = req.location.strip()
        if req.preferred_language is not None:
            user.preferred_language = req.preferred_language.strip()
        if req.farm_name is not None:
            user.farm_name = req.farm_name.strip()
        if req.main_crop is not None:
            user.main_crop = req.main_crop.strip()
        if req.farm_size is not None:
            user.farm_size = req.farm_size.strip()
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def save_profile_photo(db: Session, user: User, file_bytes: bytes, original_filename: str, content_type: str) -> User:
        import os
        from PIL import Image
        import io

        # 1. Size check (5MB max)
        MAX_SIZE = 5 * 1024 * 1024
        if len(file_bytes) > MAX_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File size exceeds maximum limit of 5MB."
            )

        # 2. Extension check
        allowed_exts = {".jpg", ".jpeg", ".png", ".webp"}
        _, ext = os.path.splitext(original_filename.lower())
        if ext not in allowed_exts:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file extension '{ext}'. Allowed: .jpg, .jpeg, .png, .webp"
            )

        # 3. MIME check
        allowed_mimes = {"image/jpeg", "image/jpg", "image/png", "image/webp"}
        if content_type.lower() not in allowed_mimes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid image content type '{content_type}'."
            )

        # 4. PIL validation
        try:
            img = Image.open(io.BytesIO(file_bytes))
            img.verify()
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Corrupted or invalid image file."
            )

        # 5. Clean up old custom photo if exists
        profile_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads", "profile")
        os.makedirs(profile_dir, exist_ok=True)

        if user.profile_photo_url and user.profile_photo_url.startswith("/uploads/profile/"):
            old_filename = os.path.basename(user.profile_photo_url)
            old_path = os.path.join(profile_dir, old_filename)
            if os.path.exists(old_path):
                try:
                    os.remove(old_path)
                except Exception as e:
                    print(f"[AuthService] Error removing old photo {old_path}: {e}")

        # 6. Save new photo
        clean_ext = ext if ext != ".jpeg" else ".jpg"
        unique_name = f"user_{user.id}_{uuid.uuid4().hex[:10]}{clean_ext}"
        new_file_path = os.path.join(profile_dir, unique_name)
        with open(new_file_path, "wb") as f:
            f.write(file_bytes)

        user.profile_photo_url = f"/uploads/profile/{unique_name}"
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def delete_profile_photo(db: Session, user: User) -> User:
        import os
        profile_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads", "profile")
        if user.profile_photo_url and user.profile_photo_url.startswith("/uploads/profile/"):
            old_filename = os.path.basename(user.profile_photo_url)
            old_path = os.path.join(profile_dir, old_filename)
            if os.path.exists(old_path):
                try:
                    os.remove(old_path)
                except Exception as e:
                    print(f"[AuthService] Error removing photo {old_path}: {e}")

        user.profile_photo_url = None
        db.commit()
        db.refresh(user)
        return user
