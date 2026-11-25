import logging
from fastapi import Request
from fastapi.responses import JSONResponse
from typing import Any
from fastapi.exceptions import RequestValidationError


logger = logging.getLogger("vantage360-ai")

class AppException(Exception):
    def __init__(self,
                 code: str,
                 message: str,
                 status_code: int = 400,
                 *,
                 tool: str | None = None,
                 version: str | None = None,
                 input_data: dict[str, Any] | None = None,
                 details: dict[str, Any] | None = None,

                 ):
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code
        self.tool = tool
        self.version = version
        self.input_data = input_data or {}
        self.details = details or {}


def build_error_response(
        *,
        code: str,
        message: str,
        status_code: int,
        tool: str = "unknown",
        version: str = "unknown",
        input_data: dict[str, Any] | None = None,
        details: dict[str, Any] | None = None,
):

    error = {
        "code": code,
        "message": message,
    }

    if details:
        error["details"] = details

    return JSONResponse(
        status_code=status_code,
        content={
            "tool": tool,
            "version": version,
            "input": input_data or {},
            "output": {},
            "status": "error",
            "error": error,
        },
    )

    """Handling every expected error anywhere in the app"""
def register_error_handlers(app):
    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException):
        logger.warning("Handled application error: "
                       "code=%s message=%s path=%s",
                       exc.code,
                       exc.message,
                       request.url.path,
                       )
        return build_error_response(
            code=exc.code,
            message=exc.message,
            status_code=exc.status_code,
            tool=exc.tool or "unknown",
            version=exc.version or "unknown",
            input_data=exc.input_data,
            details=exc.details,
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
            request: Request,
            exc: RequestValidationError,
    ):
        logger.warning(
            "Request validation failed: path=%s",
            request.url.path,
        )

        return build_error_response(
            code="VALIDATION_ERROR",
            message="Invalid request input.",
            status_code=422,
            details={
                "validation_errors": exc.errors(),
            },
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(
            request: Request,
            exc: Exception,
    ):
        logger.exception(
            "Unhandled application error: path=%s",
            request.url.path,
        )

        return build_error_response(
            code="INTERNAL_ERROR",
            message="An unexpected internal error occurred.",
            status_code=500,
        )


