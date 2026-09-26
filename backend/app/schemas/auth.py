"""Pydantic schemas for user authentication and authorization."""

from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class UserRegisterRequest(BaseModel):
    """Registration request payload."""

    email: EmailStr
    password: str = Field(min_length=6, description="User password (min 6 characters)")
    name: Optional[str] = Field(default=None, max_length=100)


class UserLoginRequest(BaseModel):
    """Login credentials request payload."""

    email: EmailStr
    password: str = Field(min_length=1)


class AuthTokenResponse(BaseModel):
    """Authentication token response payload."""

    access_token: str
    token_type: str = "bearer"
    user_id: str
    email: EmailStr


class UserProfileResponse(BaseModel):
    """User profile response payload."""

    id: str
    email: EmailStr
    name: Optional[str] = None
    created_at: Optional[str] = None
