"""
Profile Management API Endpoints
Handles user profile retrieval and updates.

Spec Reference: specs/002-dashboard-ux-enhancements/spec.md (FR-001, FR-002)
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlmodel import Session
from datetime import datetime, UTC

from app.db.session import get_session
from app.models.user import User
from app.schemas.auth import UserResponse, ProfileUpdateRequest
from app.schemas.user import UserRead
from app.auth.dependencies import get_current_user
from app.services.storage import storage_service

router = APIRouter(prefix="/profile", tags=["profile"])


@router.get("", response_model=UserRead)
async def get_profile(
    current_user: User = Depends(get_current_user)
):
    """
    Get current user's profile information.

    Returns user data including name, profile picture, and email.

    Spec: specs/002-dashboard-ux-enhancements/spec.md (FR-002)

    Returns:
        UserRead: User profile data

    Raises:
        401: If user is not authenticated
    """
    return current_user


@router.put("", response_model=UserRead)
async def update_profile(
    profile_data: ProfileUpdateRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Update current user's profile information.

    Allows updating name and profile_picture URL.
    Email cannot be changed through this endpoint.

    Spec: specs/002-dashboard-ux-enhancements/spec.md (FR-002)

    Args:
        profile_data: Profile fields to update (name, profile_picture)
        current_user: Authenticated user from JWT
        session: Database session

    Returns:
        UserRead: Updated user profile data

    Raises:
        401: If user is not authenticated
        400: If validation fails
    """
    # Update fields if provided
    if profile_data.name is not None:
        current_user.name = profile_data.name

    if profile_data.profile_picture is not None:
        current_user.profile_picture = profile_data.profile_picture

    # Update timestamp
    current_user.updated_at = datetime.now(UTC)

    # Save to database
    session.add(current_user)
    session.commit()
    session.refresh(current_user)

    return current_user


@router.post("/upload-picture", response_model=UserRead)
async def upload_profile_picture(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Upload profile picture to cloud storage and update user profile.

    Uploads image to S3/R2 and automatically updates user's profile_picture field.

    Spec: specs/002-dashboard-ux-enhancements/spec.md (FR-003, FR-042, FR-045)

    Args:
        file: Image file (JPEG, PNG, GIF, WebP - max 5MB)
        current_user: Authenticated user from JWT
        session: Database session

    Returns:
        UserRead: Updated user profile with new picture URL

    Raises:
        400: Invalid file type or size exceeds 5MB
        401: If user is not authenticated
        503: Cloud storage not configured
        500: Upload failed
    """
    # Upload to cloud storage
    picture_url = await storage_service.upload_profile_picture(file, current_user.id)

    # Update user profile with new URL
    current_user.profile_picture = picture_url
    current_user.updated_at = datetime.now(UTC)

    session.add(current_user)
    session.commit()
    session.refresh(current_user)

    return current_user
