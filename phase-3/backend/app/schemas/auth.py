"""
Authentication Pydantic Schemas
Defines request and response models for authentication endpoints.

Spec Reference: specs/api/rest-endpoints.md (Authentication Endpoints)
"""

from pydantic import BaseModel, EmailStr, Field
from datetime import datetime


class UserRegisterRequest(BaseModel):
    """
    Request schema for user registration.

    Endpoint: POST /api/auth/register
    Spec: specs/api/rest-endpoints.md
    """

    email: EmailStr = Field(
        ...,
        description="User email address (login identifier)",
        examples=["user@example.com"]
    )
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="User password (min 8 chars, max 128 chars)",
        examples=["SecurePass123!"]
    )
    name: str | None = Field(
        default=None,
        max_length=255,
        description="Display name (optional, defaults to email prefix if not provided)",
        examples=["John Doe"]
    )

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "SecurePass123!",
                "name": "John Doe"
            }
        }


class UserLoginRequest(BaseModel):
    """
    Request schema for user login.

    Endpoint: POST /api/auth/login
    Spec: specs/api/rest-endpoints.md
    """

    email: EmailStr = Field(
        ...,
        description="User email address",
        examples=["user@example.com"]
    )
    password: str = Field(
        ...,
        description="User password",
        examples=["SecurePass123!"]
    )

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "SecurePass123!"
            }
        }


class UserBasicInfo(BaseModel):
    """
    Basic user information included in login response.
    """
    id: int
    email: str
    name: str | None = None
    profile_picture: str | None = None

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """
    Response schema for successful login.

    Contains JWT access token, metadata, and user information.
    Spec: specs/api/rest-endpoints.md (POST /api/auth/login response)
    """

    access_token: str = Field(
        ...,
        description="JWT access token",
        examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."]
    )
    token_type: str = Field(
        default="Bearer",
        description="Token type (always 'Bearer')",
        examples=["Bearer"]
    )
    expires_in: int = Field(
        ...,
        description="Token expiry time in seconds",
        examples=[86400]
    )
    user: UserBasicInfo = Field(
        ...,
        description="User information"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "Bearer",
                "expires_in": 86400,
                "user": {
                    "id": 1,
                    "email": "user@example.com",
                    "name": "John Doe",
                    "profile_picture": None
                }
            }
        }


class UserResponse(BaseModel):
    """
    Response schema for user data (without password).

    Used for registration response and user profile.
    Spec: specs/api/rest-endpoints.md (POST /api/auth/register response)
    """

    id: int = Field(
        ...,
        description="User ID",
        examples=[1]
    )
    email: str = Field(
        ...,
        description="User email address",
        examples=["user@example.com"]
    )
    name: str | None = Field(
        default=None,
        description="User display name",
        examples=["John Doe"]
    )
    profile_picture: str | None = Field(
        default=None,
        description="Profile picture URL (cloud storage)",
        examples=["https://cdn.example.com/profiles/user123.jpg"]
    )
    created_at: datetime = Field(
        ...,
        description="Account creation timestamp",
        examples=["2025-12-30T10:00:00Z"]
    )

    class Config:
        from_attributes = True  # Enable ORM mode for SQLModel compatibility
        json_schema_extra = {
            "example": {
                "id": 1,
                "email": "user@example.com",
                "name": "John Doe",
                "profile_picture": "https://cdn.example.com/profiles/user123.jpg",
                "created_at": "2025-12-30T10:00:00Z"
            }
        }


class ProfileUpdateRequest(BaseModel):
    """
    Request schema for updating user profile.

    Endpoint: PUT /api/v1/profile
    Spec: specs/002-dashboard-ux-enhancements/spec.md (FR-002)
    """

    name: str | None = Field(
        default=None,
        max_length=255,
        description="User display name",
        examples=["John Doe"]
    )
    profile_picture: str | None = Field(
        default=None,
        max_length=500,
        description="Profile picture URL (cloud storage)",
        examples=["https://cdn.example.com/profiles/user123.jpg"]
    )

    class Config:
        json_schema_extra = {
            "example": {
                "name": "John Doe",
                "profile_picture": "https://cdn.example.com/profiles/user123.jpg"
            }
        }
