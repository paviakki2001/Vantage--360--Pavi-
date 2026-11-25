import logging
import time
import uuid

from fastapi import Request
from fastapi.responses import JSONResponse

from api.app.config import settings
from api.app.gateway.rate_limiter import RateLimiter
from api.app.observability.metrics import metrics

logger = logging.getLogger("vantage360-ai")
MAX_REQUEST_BODY_BYTES = 512 * 1024

rate_limiter = RateLimiter(
    max_requests=settings.gateway_rate_limit,
    window_seconds=settings.gateway_rate_window_seconds,
)


async def gateway_middleware(
        request: Request,
        call_next,
):

    request_id = request.headers.get(
        "X-Request-ID"
    ) or str(uuid.uuid4())

    # Request body size validation
    content_length = request.headers.get("content-length")

    if content_length is not None:
        try:
            body_size = int(content_length)
        except ValueError:
            return JSONResponse(
                status_code=400,
                content={
                    "error": {
                        "code": "INVALID_CONTENT_LENGTH",
                        "message": "Invalid Content-Length header.",
                    },
                    "request_id": request_id,
                },
                headers={"X-Request-ID": request_id},
            )

        if body_size < 0:
            return JSONResponse(
                status_code=400,
                content={
                    "error": {
                        "code": "INVALID_CONTENT_LENGTH",
                        "message": "Invalid Content-Length header.",
                    },
                    "request_id": request_id,
                },
                headers={"X-Request-ID": request_id},
            )

        if body_size > MAX_REQUEST_BODY_BYTES:
            logger.warning(
                "Request body too large request_id=%s path=%s size=%s",
                request_id,
                request.url.path,
                body_size,
            )

            return JSONResponse(
                status_code=413,
                content={
                    "error": {
                        "code": "PAYLOAD_TOO_LARGE",
                        "message": "Request body exceeds the allowed size.",
                    },
                    "request_id": request_id,
                },
                headers={"X-Request-ID": request_id},
            )

    request.state.request_id = request_id

    start_time = time.perf_counter()

    client_ip = (
        request.client.host
        if request.client
        else "unknown"
    )

    # Rate limiting
    if request.url.path.startswith(
            settings.api_v2_prefix
    ):

        if not rate_limiter.is_allowed(
                client_ip
        ):

            logger.warning(
                "Rate limit exceeded "
                "request_id=%s client=%s path=%s",
                request_id,
                client_ip,
                request.url.path,
            )

            return JSONResponse(
                status_code=429,
                content={
                    "error": {
                        "code": "RATE_LIMIT_EXCEEDED",
                        "message": (
                            "Too many requests. "
                            "Please try again later."
                        ),
                    },
                    "request_id": request_id,
                },
                headers={
                    "X-Request-ID": request_id,
                    "Retry-After": str(
                        settings.gateway_rate_window_seconds
                    ),
                },
            )

    try:

        response = await call_next(request)

    except Exception:

        logger.exception(
            "Unhandled gateway exception "
            "request_id=%s method=%s path=%s",
            request_id,
            request.method,
            request.url.path,
        )

        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "Internal server error.",
                },
                "request_id": request_id,
            },
            headers={
                "X-Request-ID": request_id,
            },
        )

    duration_ms = (
                          time.perf_counter() - start_time
                  ) * 1000

    metrics.record_request(
        latency_ms=duration_ms,
        status_code=response.status_code,
    )

    logger.info(
        "API request completed "
        "request_id=%s method=%s path=%s "
        "status=%s duration_ms=%.2f client=%s",
        request_id,
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
        client_ip,
    )

    response.headers[
        "X-Request-ID"
    ] = request_id

    return response