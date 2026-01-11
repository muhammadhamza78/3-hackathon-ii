# """
# Authentication Dependencies
# FastAPI dependency functions for JWT token validation and user extraction.

# Spec Reference: specs/features/plans/authentication-plan.md (Section 2.3)
# """

# from fastapi import Depends, HTTPException, status
# from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
# from jose import JWTError
# from sqlmodel import Session, select
# from app.auth.jwt import verify_token
# from app.db.session import get_session
# from app.models.user import User


# # HTTP Bearer token security scheme
# # Automatically extracts "Authorization: Bearer <token>" header
# security = HTTPBearer()


# async def get_current_user_id(
#     credentials: HTTPAuthorizationCredentials = Depends(security)
# ) -> int:
#     """
#     FastAPI dependency to extract and validate user_id from JWT token.

#     This dependency:
#     1. Extracts token from Authorization header (via HTTPBearer)
#     2. Verifies token signature and expiry
#     3. Extracts user_id from 'sub' claim
#     4. Returns user_id as integer

#     Spec Requirement: specs/features/authentication.md (FR3, FR4)

#     Args:
#         credentials: Automatically injected by HTTPBearer dependency

#     Returns:
#         int: Authenticated user's ID

#     Raises:
#         HTTPException 401: If token is missing, invalid, expired, or malformed

#     Example Usage:
#         @router.get("/api/tasks")
#         async def list_tasks(user_id: int = Depends(get_current_user_id)):
#             # user_id is guaranteed to be valid and authenticated
#             tasks = get_user_tasks(user_id)
#             return tasks

#     Error Cases (all raise 401):
#     - Missing Authorization header
#     - Invalid header format (not "Bearer <token>")
#     - Invalid token signature
#     - Expired token
#     - Malformed token
#     - Missing 'sub' claim
#     - Invalid 'sub' value (not convertible to int)
#     """
#     token = credentials.credentials

#     try:
#         # Verify token signature and expiry
#         # Raises JWTError if invalid, expired, or malformed
#         payload = verify_token(token)

#         # Extract user_id from 'sub' claim
#         # JWT spec requires 'sub' to be string, so we convert to int
#         user_id_str = payload.get("sub")

#         if not user_id_str:
#             # Token missing 'sub' claim
#             raise HTTPException(
#                 status_code=status.HTTP_401_UNAUTHORIZED,
#                 detail="Unauthorized"
#             )

#         # Convert string to integer
#         try:
#             user_id = int(user_id_str)
#         except ValueError:
#             # 'sub' claim is not a valid integer
#             raise HTTPException(
#                 status_code=status.HTTP_401_UNAUTHORIZED,
#                 detail="Unauthorized"
#             )

#         return user_id

#     except JWTError:
#         # Token verification failed (invalid signature, expired, malformed)
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Unauthorized"
#         )


# async def get_current_user(
#     user_id: int = Depends(get_current_user_id),
#     session: Session = Depends(get_session)
# ) -> User:
#     """
#     FastAPI dependency to get the full User object from JWT token.

#     This dependency:
#     1. Extracts user_id via get_current_user_id dependency
#     2. Queries database for the User record
#     3. Returns the full User object

#     Args:
#         user_id: User ID from JWT token (injected by get_current_user_id)
#         session: Database session

#     Returns:
#         User: Full authenticated user object

#     Raises:
#         HTTPException 401: If user not found in database

#     Example Usage:
#         @router.get("/api/profile")
#         async def get_profile(current_user: User = Depends(get_current_user)):
#             return {"name": current_user.name, "email": current_user.email}
#     """
#     statement = select(User).where(User.id == user_id)
#     user = session.exec(statement).first()

#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="User not found"
#         )

#     return user








# from fastapi import Depends, HTTPException, status
# from fastapi.security import OAuth2PasswordBearer
# from app.db.models import User
# from app.db.session import get_db
# from sqlalchemy.orm import Session
# from app.auth.jwt import decode_jwt  # your JWT decode function

# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

# async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
#     credentials_exception = HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         detail="Could not validate credentials",
#         headers={"WWW-Authenticate": "Bearer"},
#     )
#     try:
#         payload = decode_jwt(token)
#         user_id = payload.get("sub")
#         if user_id is None:
#             raise credentials_exception
#     except:
#         raise credentials_exception

#     user = db.query(User).filter(User.id == user_id).first()
#     if user is None:
#         raise credentials_exception
#     return user















"""
Authentication Dependencies
FastAPI dependency functions for JWT token validation and user extraction.

Spec Reference: specs/features/plans/authentication-plan.md (Section 2.3)
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError
from sqlmodel import Session, select

from app.auth.jwt import verify_token
from app.db.session import get_session
from app.models.user import User

# -----------------------------
# Security scheme (Bearer token)
# -----------------------------
security = HTTPBearer()


# -----------------------------
# Dependency: Extract user_id
# -----------------------------
async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> int:
    """
    FastAPI dependency to extract and validate user_id from JWT token.

    Raises:
        HTTPException 401: If token is missing, invalid, expired, or malformed

    Returns:
        int: Authenticated user's ID
    """
    token = credentials.credentials

    try:
        # Verify token signature and expiry
        payload = verify_token(token)

        # Extract user_id from 'sub' claim
        user_id_str = payload.get("sub")
        if not user_id_str:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Unauthorized: Missing 'sub' claim in token"
            )

        # Convert to integer
        try:
            user_id = int(user_id_str)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Unauthorized: Invalid 'sub' claim"
            )

        return user_id

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized: Invalid or expired token"
        )


# -----------------------------
# Dependency: Get full User object
# -----------------------------
async def get_current_user(
    user_id: int = Depends(get_current_user_id),
    session: Session = Depends(get_session)
) -> User:
    """
    FastAPI dependency to get the full User object from JWT token.

    Raises:
        HTTPException 401: If user not found in database

    Returns:
        User: Full authenticated user object
    """
    statement = select(User).where(User.id == user_id)
    user = session.exec(statement).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    return user
