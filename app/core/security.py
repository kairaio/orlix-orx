import secrets

from fastapi import Header, HTTPException, status

from app.core.config import settings


def require_admin_key(x_orx_admin_key: str = Header(...)) -> None:
    if settings.admin_api_key == "change-me-in-production":
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="ADMIN_API_KEY is not configured",
        )
    if not secrets.compare_digest(x_orx_admin_key, settings.admin_api_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin API key",
        )
