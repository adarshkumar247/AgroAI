from typing import Optional
import re
from pydantic import BaseModel, Field, field_validator

EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

class UserRegisterRequest(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=100)
    email: str = Field(..., min_length=5, max_length=150)
    password: str = Field(..., min_length=6, max_length=100)
    confirm_password: Optional[str] = None
    location: Optional[str] = "Lucknow Farm, Uttar Pradesh"
    preferred_language: Optional[str] = "English (EN)"

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        v = v.strip().lower()
        if not EMAIL_REGEX.match(v):
            raise ValueError("Invalid email format")
        return v

class UserLoginRequest(BaseModel):
    email: str = Field(..., min_length=5, max_length=150)
    password: str
    remember_me: Optional[bool] = True

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        v = v.strip().lower()
        if not EMAIL_REGEX.match(v):
            raise ValueError("Invalid email format")
        return v

class UserResponse(BaseModel):
    id: str
    full_name: str
    email: str
    location: Optional[str] = None
    preferred_language: Optional[str] = None
    profile_photo_url: Optional[str] = None
    farm_name: Optional[str] = None
    main_crop: Optional[str] = None
    farm_size: Optional[str] = None
    created_at: Optional[str] = None

    class Config:
        from_attributes = True

class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "Bearer"
    user: UserResponse

class ProfileUpdateRequest(BaseModel):
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    location: Optional[str] = None
    preferred_language: Optional[str] = None
    farm_name: Optional[str] = None
    main_crop: Optional[str] = None
    farm_size: Optional[str] = None
