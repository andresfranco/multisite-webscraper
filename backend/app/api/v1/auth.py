"""Authentication API router — register, login, profile, API keys."""
from __future__ import annotations

from datetime import datetime, timezone

import structlog
from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.config import get_settings
from app.core.security import (
    create_access_token,
    generate_api_key,
    hash_password,
    verify_password,
)
from app.database import get_session
from app.models.user import User
from app.schemas.auth import (
    ApiKeyResponse,
    PasswordChangeRequest,
    TokenResponse,
    UserLoginRequest,
    UserRegisterRequest,
    UserResponse,
)

logger = structlog.get_logger()
settings = get_settings()

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    body: UserRegisterRequest,
    session: AsyncSession = Depends(get_session),
) -> UserResponse:
    """Create a new user account."""
    # Check uniqueness
    stmt_email = select(User).where(User.email == body.email)
    if (await session.execute(stmt_email)).scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )
    stmt_uname = select(User).where(User.username == body.username)
    if (await session.execute(stmt_uname)).scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already taken",
        )

    user = User(
        email=body.email,
        username=body.username,
        hashed_password=hash_password(body.password),
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)

    logger.info("user_registered", user_id=user.id, email=user.email)
    return UserResponse.model_validate(user)


@router.post("/login", response_model=TokenResponse)
async def login(
    body: UserLoginRequest,
    session: AsyncSession = Depends(get_session),
) -> TokenResponse:
    """Authenticate and return a JWT access token."""
    stmt = select(User).where(User.email == body.email)
    user = (await session.execute(stmt)).scalar_one_or_none()

    if user is None or not verify_password(body.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated",
        )

    # Update last login timestamp
    user.last_login_at = datetime.now(timezone.utc)
    await session.commit()

    token = create_access_token(subject=user.id)
    logger.info("user_login", user_id=user.id)

    return TokenResponse(
        access_token=token,
        expires_in=settings.access_token_expire_minutes * 60,
        user=UserResponse.model_validate(user),
    )


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)) -> UserResponse:
    """Return the profile of the authenticated user."""
    return UserResponse.model_validate(current_user)


@router.post("/change-password", status_code=status.HTTP_200_OK)
async def change_password(
    body: PasswordChangeRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> None:
    """Change the password for the currently authenticated user."""
    if not verify_password(body.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect",
        )
    current_user.hashed_password = hash_password(body.new_password)
    await session.commit()
    logger.info("password_changed", user_id=current_user.id)


@router.post("/api-key", response_model=ApiKeyResponse)
async def create_api_key(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ApiKeyResponse:
    """Generate (or regenerate) an API key for the current user."""
    new_key = generate_api_key()
    current_user.api_key = new_key
    await session.commit()
    logger.info("api_key_generated", user_id=current_user.id)
    return ApiKeyResponse(api_key=new_key)


@router.delete("/api-key", status_code=status.HTTP_200_OK)
async def revoke_api_key(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> None:
    """Revoke the current user's API key."""
    current_user.api_key = None
    await session.commit()
    logger.info("api_key_revoked", user_id=current_user.id)
