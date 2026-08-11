from fastapi import FastAPI

from app.api.health import router as health_router
from app.api.orx import router as orx_router
from app.core.config import settings


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "ORX is the native digital currency and economic infrastructure "
        "of the ORLIX digital world."
    ),
)


app.include_router(health_router)
app.include_router(orx_router)


@app.get("/")
def root():
    return {
        "project": "ORX",
        "full_name": "ORLIX Digital Currency",
        "network": "ORLIX",
        "version": settings.app_version,
        "status": "foundation",
        "docs": "/docs",
        "health": "/health",
        "orx": "/api/v1/orx",
    }
