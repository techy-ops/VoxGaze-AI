from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


class UserRegisterRequest(BaseModel):
    """Schema for user registration request."""
    email: EmailStr = Field(..., example="user@voxgaze.ai")
    password: str = Field(..., min_length=6, example="SecurePassword123!")
    display_name: Optional[str] = Field(None, example="Jane Doe")
    full_name: Optional[str] = Field(None, example="Jane Doe")


class UserRegisterResponse(BaseModel):
    """Schema for user registration response."""
    status: str = Field(default="success", example="success")
    user_id: str = Field(..., example="usr_voxgaze_1001")
    email: EmailStr = Field(..., example="user@voxgaze.ai")
    created_at: str = Field(..., example="2026-07-25T12:00:00Z")


class UserLoginRequest(BaseModel):
    """Schema for user login request."""
    email: EmailStr = Field(..., example="user@voxgaze.ai")
    password: str = Field(..., example="SecurePassword123!")


class TokenResponse(BaseModel):
    """Schema for authentication token response."""
    status: str = Field(default="success", example="success")
    access_token: str = Field(..., example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...")
    refresh_token: str = Field(..., example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...")
    token_type: str = Field(default="Bearer", example="Bearer")
    expires_in: int = Field(default=3600, example=3600)


class TokenRefreshRequest(BaseModel):
    """Schema for token refresh request."""
    refresh_token: str = Field(..., example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...")


class LogoutRequest(BaseModel):
    """Schema for user logout request."""
    refresh_token: str = Field(..., example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...")


class ActionResponse(BaseModel):
    """Schema for general action success responses (logout, forgot password, email verification)."""
    status: str = Field(default="success", example="success")
    message: str = Field(..., example="Action completed successfully.")


class ForgotPasswordRequest(BaseModel):
    """Schema for requesting password reset link."""
    email: EmailStr = Field(..., example="user@voxgaze.ai")


class VerifyEmailRequest(BaseModel):
    """Schema for requesting email verification link."""
    email: EmailStr = Field(..., example="user@voxgaze.ai")


class UserProfileResponse(BaseModel):
    """Schema for complete Firestore user profile."""
    status: str = Field(default="success", example="success")
    user_id: str = Field(..., example="usr_voxgaze_1001")
    email: EmailStr = Field(..., example="user@voxgaze.ai")
    display_name: str = Field(default="Jane Doe", example="Jane Doe")
    created_at: str = Field(..., example="2026-07-25T12:00:00Z")
    last_login: str = Field(..., example="2026-07-25T12:30:00Z")
    role: str = Field(default="user", example="user")
    preferred_language: str = Field(default="en", example="en")
    accessibility_preferences: Dict[str, Any] = Field(
        default_factory=lambda: {
            "high_contrast": True,
            "font_size": "large",
            "speech_rate": 1.0,
            "gaze_sensitivity": 0.8,
        }
    )
    emergency_contacts: List[Dict[str, str]] = Field(default_factory=list)
    settings: Dict[str, Any] = Field(default_factory=dict)
    profile_completed: bool = Field(default=True, example=True)


class UserResponse(BaseModel):
    """Backwards compatible schema for user response."""
    status: str = Field(default="success", example="success")
    user_id: str = Field(..., example="usr_voxgaze_1001")
    email: EmailStr = Field(..., example="user@voxgaze.ai")
    full_name: Optional[str] = Field("Jane Doe", example="Jane Doe")
