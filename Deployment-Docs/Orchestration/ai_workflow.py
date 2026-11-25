import re

from orchestration.workflows.tool_register import get_tool

import logging

logger = logging.getLogger("vantage360-ai")


class AIWorkflow:

    def __init__(self, churn_service):
        self.churn_service = churn_service

    def process_question(self, question: str, correlation_id: str | None = None,) -> dict:
        """
        Process a customer question and return a structured
        business-oriented response.
        """

        if not question or not question.strip():
            raise ValueError("Question is required.")

        normalized_question = question.strip()

        # 1. Detect churn intent
        if not self._is_churn_question(normalized_question):
            raise ValueError(
                "The question is not a supported churn question."
            )

        # 2. Extract customer ID
        customer_id = self._extract_customer_id(normalized_question)

        if not customer_id:
            raise ValueError(
                "A valid customer_id could not be found in the question."
            )
        logger.info(
            "workflow_started correlation_id=%s customer_id=%s",
            correlation_id,
            customer_id,
        )

        # 3. Get registered churn tool
        tool = get_tool("churn_risk")

        if not tool:
            raise RuntimeError(
                "Churn tool is not registered."
            )

        if not tool["enabled"]:
            raise RuntimeError(
                "Churn tool is disabled."
            )

        # 4. Execute churn prediction
        prediction = self.churn_service.predict(customer_id,  correlation_id=correlation_id,)

        # Validate downstream tool response
        self._validate_prediction(prediction)

        logger.info(
            "workflow_completed correlation_id=%s customer_id=%s",
            correlation_id,
            customer_id,
        )

        # 5. Create business explanation
        explanation = self._build_business_explanation(
            customer_id=customer_id,
            prediction=prediction,
        )

        # 6. Return structured workflow result
        return {
            "correlation_id": correlation_id,
            "question": normalized_question,
            "tool": "churn_risk",
            "tool_version": tool["version"],
            "customer_id": customer_id,
            "prediction": prediction,
            "business_explanation": explanation,
        }

    @staticmethod
    def _is_churn_question(question: str) -> bool:
        """
        Determine whether the question is related to churn risk.
        """

        churn_keywords = [
            "churn",
            "churning",
            "attrition",
            "leave",
            "leaving",
            "risk",
        ]

        question_lower = question.lower()

        return any(
            keyword in question_lower
            for keyword in churn_keywords
        )

    @staticmethod
    def _extract_customer_id(question: str) -> str | None:
        """
        Extract a customer ID such as CUST00001 from the question.
        """

        match = re.search(
            r"\bCUST\d+\b",
            question.upper(),
        )

        if not match:
            return None

        return match.group(0)

    @staticmethod
    def _build_business_explanation(
            customer_id: str,
            prediction: dict,
    ) -> str:
        """
        Convert the structured model output into a simple
        business-oriented explanation.
        """

        risk_score = prediction.get("risk_score")
        risk_category = prediction.get("risk_category")

        if risk_score is not None:
            percentage = round(float(risk_score) * 100, 2)

            return (
                f"Customer {customer_id} is classified as "
                f"{risk_category} churn risk, with an estimated "
                f"risk score of {percentage}%."
            )

        return (
            f"Customer {customer_id} is classified as "
            f"{risk_category} churn risk."
        )

    @staticmethod
    def _validate_prediction(prediction: dict) -> None:
        """
        Validate the structured response returned by the churn tool.
        """

        if not isinstance(prediction, dict):
            raise ValueError(
                "The churn tool returned an invalid response."
            )

        required_fields = [
            "prediction",
            "risk_score",
            "risk_category",
            "model_version",
        ]

        missing_fields = [
            field
            for field in required_fields
            if field not in prediction
        ]

        if missing_fields:
            raise ValueError(
                "The churn tool response is missing required fields."
            )

        try:
            risk_score = float(prediction["risk_score"])
        except (TypeError, ValueError) as exc:
            raise ValueError(
                "The churn tool returned an invalid risk score."
            ) from exc

        if not 0 <= risk_score <= 1:
            raise ValueError(
                "The churn tool returned an invalid risk score."
            )

        if prediction["risk_category"] not in {
            "Low",
            "Medium",
            "High",
        }:
            raise ValueError(
                "The churn tool returned an invalid risk category."
            )


