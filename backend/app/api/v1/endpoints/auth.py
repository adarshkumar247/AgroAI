from fastapi import APIRouter, Depends, UploadFile, File, status
from sqlalchemy.orm import Session

from backend.app.database.session import get_db
from backend.app.schemas.auth import (
    UserRegisterRequest,
    UserLoginRequest,
    UserResponse,
    AuthResponse,
    ProfileUpdateRequest
)
from backend.app.services.auth_service import AuthService
from backend.app.core.security import get_current_user, extract_token
from backend.app.models.user import User

router = APIRouter()

def _to_user_response(user: User) -> UserResponse:
    return UserResponse(
        id=user.id,
        full_name=user.full_name,
        email=user.email,
        location=user.location,
        preferred_language=user.preferred_language,
        profile_photo_url=user.profile_photo_url,
        farm_name=user.farm_name,
        main_crop=user.main_crop,
        farm_size=user.farm_size,
        created_at=user.created_at.isoformat() if user.created_at else None
    )

@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def register(req: UserRegisterRequest, db: Session = Depends(get_db)):
    """Register a new farmer account and issue an authentication session token."""
    user, token = AuthService.register_user(db, req)
    return AuthResponse(
        access_token=token,
        token_type="Bearer",
        user=_to_user_response(user)
    )

@router.post("/login", response_model=AuthResponse)
def login(req: UserLoginRequest, db: Session = Depends(get_db)):
    """Authenticate with email and password to receive an access token."""
    user, token = AuthService.authenticate_user(db, req.email, req.password)
    return AuthResponse(
        access_token=token,
        token_type="Bearer",
        user=_to_user_response(user)
    )

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """Return the profile of the currently authenticated farmer."""
    return _to_user_response(current_user)

@router.post("/logout")
def logout(
    token: str = Depends(extract_token),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Invalidate current farmer session token."""
    AuthService.logout_user(db, token)
    return {"status": "ok", "message": "Successfully logged out"}

@router.put("/profile", response_model=UserResponse)
def update_profile(
    req: ProfileUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update profile settings for the currently authenticated farmer."""
    updated = AuthService.update_profile(db, current_user, req)
    return _to_user_response(updated)

@router.post("/profile/photo", response_model=UserResponse)
async def upload_profile_photo(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Upload or update profile photo for current user."""
    contents = await file.read()
    updated = AuthService.save_profile_photo(
        db=db,
        user=current_user,
        file_bytes=contents,
        original_filename=file.filename or "photo.jpg",
        content_type=file.content_type or "image/jpeg"
    )
    return _to_user_response(updated)

@router.delete("/profile/photo", response_model=UserResponse)
def delete_profile_photo(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Remove custom profile photo for current user and revert to default avatar."""
    updated = AuthService.delete_profile_photo(db, current_user)
    return _to_user_response(updated)
