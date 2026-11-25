from api.app.errors import AppException


class ModelServiceUnavailableError(AppException):
    def __init__(
            self,
            *,
            tool: str,
            version: str,
            message: str = "Model service is unavailable.",
    ):
        super().__init__(
            code="MODEL_SERVICE_UNAVAILABLE",
            message=message,
            status_code=503,
            tool=tool,
            version=version,
        )


class PredictionTimeoutError(AppException):
    def __init__(
            self,
            *,
            tool: str,
            version: str,
            message: str = "Model prediction timed out.",
    ):
        super().__init__(
            code="TIMEOUT_ERROR",
            message=message,
            status_code=504,
            tool=tool,
            version=version,
        )


class DependencyFailureError(AppException):
    def __init__(
            self,
            *,
            tool: str,
            version: str,
            message: str = "A required dependency failed.",
            details: dict | None = None,
    ):
        super().__init__(
            code="DEPENDENCY_ERROR",
            message=message,
            status_code=503,
            tool=tool,
            version=version,
            details=details,
        )


class ModelPredictionError(AppException):
    def __init__(
            self,
            *,
            tool: str,
            version: str,
            message: str = "Model prediction failed.",
    ):
        super().__init__(
            code="MODEL_ERROR",
            message=message,
            status_code=500,
            tool=tool,
            version=version,
        )


class OrchestratorFailureError(AppException):
    def __init__(
            self,
            *,
            tool: str,
            version: str,
            message: str = "Orchestration workflow failed.",
            details: dict | None = None,
    ):
        super().__init__(
            code="ORCHESTRATOR_ERROR",
            message=message,
            status_code=502,
            tool=tool,
            version=version,
            details=details,
        )