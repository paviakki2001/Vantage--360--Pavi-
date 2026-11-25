from fastapi import APIRouter
from api.app.config import settings

router = APIRouter(prefix="/health",tags=["System"])


@router.get("")
def health():
    return {
        "status": "healthy",
        "service": settings.service_name
    }


