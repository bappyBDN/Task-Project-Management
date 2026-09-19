"""Lightweight header-based authentication for the MVP.

The current user is resolved from the `X-User-Id` header (no passwords yet).
`require_admin` enforces that the caller has the `admin` role.
"""
from fastapi import Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app import models
from app.database import get_db

ADMIN_ROLE = "admin"


def get_current_user(
    x_user_id: int | None = Header(default=None, alias="X-User-Id"),
    db: Session = Depends(get_db),
) -> models.User:
    if x_user_id is None:
        raise HTTPException(status_code=401, detail="Missing X-User-Id header")
    user = db.get(models.User, x_user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="Unknown or inactive user")
    return user


def get_admin_user(user: models.User = Depends(get_current_user)) -> models.User:
    if user.role != ADMIN_ROLE:
        raise HTTPException(status_code=403, detail="Admin role required")
    return user
