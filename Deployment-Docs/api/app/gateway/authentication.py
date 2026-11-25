from fastapi import Header, HTTPException

from api.app.config import settings


def require_api_key(
        x_api_key: str | None = Header(
            default=None,
            alias="X-API-Key",
        ),
) -> None:

    if not settings.gateway_auth_enabled:
        return

    if settings.gateway_api_key is None:
        raise HTTPException(
            status_code=500,
            detail={
                "code": "AUTH_CONFIGURATION_ERROR",
                "message": "API authentication is not configured.",
            },
        )

    if x_api_key is None:
        raise HTTPException(
            status_code=401,
            detail={
                "code": "AUTHENTICATION_REQUIRED",
                "message": "Missing API key.",
            },
            headers={
                "WWW-Authenticate": "ApiKey",
            },
        )
    expected_key = (
        settings.gateway_api_key.get_secret_value()
    )

    if x_api_key != expected_key:
        raise HTTPException(
            status_code=401,
            detail={
                "code": "INVALID_API_KEY",
                "message": "Invalid API key.",
            },
            headers={
                "WWW-Authenticate": "ApiKey",
            },
        )
