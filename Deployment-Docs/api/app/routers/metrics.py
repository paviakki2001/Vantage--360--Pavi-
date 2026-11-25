from fastapi import APIRouter

from api.app.observability.metrics import metrics


router = APIRouter(
    prefix="/metrics",
    tags=["Observability"],
)


@router.get("")
def get_metrics():
    return metrics.snapshot()