import logging
from typing import Any

import httpx

logger = logging.getLogger("vantage360-ai")


class ServiceIntegrationError(Exception):
    """Raised when a downstream service integration fails."""

class ServiceClient:
    def __init__(
            self,
            base_url: str = "http://127.0.0.1:8000",
            timeout_seconds: float = 10.0,
            client: httpx.Client | None = None,
    ):
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds
        self.client = client

    def _post(
            self,
            path: str,
            payload: dict[str, Any],
    ) -> dict[str, Any]:

        url = f"{self.base_url}{path}"

        logger.info(
            "Calling downstream service url=%s",
            url,
        )
        try:
            if self.client is not None:
                response = self.client.post(
                    url,
                    json=payload,
                    timeout=self.timeout_seconds,
                )
            else:
                response = httpx.post(
                    url,
                    json=payload,
                    timeout=self.timeout_seconds,
                )

            response.raise_for_status()

            result = response.json()

            if not isinstance(result, dict):
                raise ServiceIntegrationError(
                    "Downstream service returned an invalid response."
                )

            return result

        except httpx.TimeoutException as exc:
            logger.error(
                "Downstream service timeout url=%s",
                url,
            )
            raise ServiceIntegrationError(
                "Downstream service timed out."
            ) from exc

        except httpx.HTTPStatusError as exc:
            logger.error(
                "Downstream service returned HTTP %s url=%s",
                exc.response.status_code,
                url,
            )
            raise ServiceIntegrationError(
                f"Downstream service returned "
                f"HTTP {exc.response.status_code}."
            ) from exc

        except httpx.RequestError as exc:
            logger.error(
                "Downstream service request failed url=%s error=%s",
                url,
                exc,
            )
            raise ServiceIntegrationError(
                "Unable to reach downstream service."
            ) from exc

    def predict_churn(
            self,
            customer_id: str,
    ) -> dict[str, Any]:

        return self._post(
            "/api/v2/churn/predict",
            {
                "customer_id": customer_id,
            },
        )

    def get_forecast(self) -> dict[str, Any]:

        return self._post(
            "/api/v2/forecast/predict",
            {},
        )

    def get_recommendation(
            self,
            customer_id: str,
    ) -> dict[str, Any]:

        return self._post(
            "/api/v2/recommendation/predict",
            {
                "customer_id": customer_id,
            },
        )