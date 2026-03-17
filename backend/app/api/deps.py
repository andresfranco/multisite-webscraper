"""FastAPI dependency for resolving the authenticated user."""
from __future__ import annotations

from typing import Optional

import structlog
from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_access_token
from app.database import get_session
from app.models.user import User

logger = structlog.get_logger()

_bearer = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(_bearer),
    x_api_key: Optional[str] = Header(default=None),
    session: AsyncSession = Depends(get_session),
) -> User:
    """Resolve the current user from a Bearer JWT or X-Api-Key header.

    Raises HTTP 401 if not authenticated.
    """
    user: Optional[User] = None

    # --- Try Bearer JWT first ---
    if credentials is not None:
        subject = decode_access_token(credentials.credentials)
        if subject is not None:
            try:
                user_id = int(subject)
                user = await session.get(User, user_id)
            except (ValueError, TypeError):
                pass

    # --- Fallback: X-Api-Key header ---
    if user is None and x_api_key:
        stmt = select(User).where(User.api_key == x_api_key)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user account",
        )

    return user


async def get_current_superuser(
    current_user: User = Depends(get_current_user),
) -> User:
    """Raise 403 unless current user is a superuser."""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Superuser access required",
        )
    return current_user
