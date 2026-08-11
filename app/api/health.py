from fastapi import APIRouter

router = APIRouter(tags=["System"])


@router.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "ORX Core",
        "version": "0.1.0",
    }
