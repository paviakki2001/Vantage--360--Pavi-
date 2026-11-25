from fastapi import FastAPI, Request
from api.app.logging_config import setup_logging, audit_logger
from api.app.config import settings
from api.app.errors import register_error_handlers
import time
import uuid
import logging
from api.app.routers import health, churn, customer_intelligence, report, forecast, recommendation, readiness, metrics
from api.app.gateway.middleware import gateway_middleware

logger = setup_logging()

app = FastAPI(title=settings.app_name)

app.middleware("http")(
    gateway_middleware
)

app.include_router(
    health.router,
    prefix=settings.api_v2_prefix
)

app.include_router(
    churn.router,
    prefix=settings.api_v2_prefix
)

app.include_router(
    forecast.router,
    prefix=settings.api_v2_prefix,
)

app.include_router(
    recommendation.router,
    prefix=settings.api_v2_prefix,
)

app.include_router(
    readiness.router,
    prefix=settings.api_v2_prefix,
)

app.include_router(
    customer_intelligence.router,
    prefix=settings.api_v2_prefix,
)

app.include_router(
    report.router,
    prefix=settings.api_v2_prefix,
)
app.include_router(
    metrics.router,
    prefix=settings.api_v2_prefix,
)

logger.info("starting %s in %s environment", settings.service_name, settings.environment)

register_error_handlers(app)

@app.middleware("http")
async def request_logging_middleware(
        request: Request,
        call_next,
):
    request_id = getattr(
        request.state,
        "request_id",
        None,
    ) or str(uuid.uuid4())
    request.state.request_id = request_id
    request.state.correlation_id = request_id

    start_time = time.perf_counter()

    logger.info(
        "request_started request_id=%s method=%s path=%s",
        request_id,
        request.method,
        request.url.path,
    )

    try:
        response = await call_next(request)

        duration_ms = (
                              time.perf_counter() - start_time
                      ) * 1000

        response.headers["X-Request-ID"] = request_id

        logger.info(
            "request_completed request_id=%s status_code=%s duration_ms=%.2f",
            request_id,
            response.status_code,
            duration_ms,
        )

        audit_logger.info(
            "request_audit request_id=%s method=%s path=%s status_code=%s",
            request_id,
            request.method,
            request.url.path,
            response.status_code,
        )

        return response

    except Exception:
        logger.exception(
            "request_failed request_id=%s method=%s path=%s",
            request_id,
            request.method,
            request.url.path,
        )

        audit_logger.error(
            "request_error_audit request_id=%s method=%s path=%s",
            request_id,
            request.method,
            request.url.path,
        )

        raise

