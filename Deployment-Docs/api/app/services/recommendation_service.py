import json
import logging
from pathlib import Path
from typing import Any

import pandas as pd

logger = logging.getLogger("vantage360-ai")


class RecommendationService:
    TOOL_NAME = "next_best_action"
    TOOL_VERSION = "v1"

    def __init__(self):
        project_root = Path(__file__).resolve().parents[3]

        self.recommendations_file = (
                project_root
                / "models"
                / "artifact"
                / "next_best_action_recommendations.csv"
        )

        self.rules_file = (
                project_root
                / "models"
                / "artifact"
                / "next_best_action_rules.json"
        )

        self.recommendations = self._load_recommendations()
        self.rules = self._load_rules()

    def _load_recommendations(self) -> pd.DataFrame:
        if not self.recommendations_file.exists():
            raise FileNotFoundError(
                "Recommendation file not found: "
                f"{self.recommendations_file}"
            )

        dataframe = pd.read_csv(
            self.recommendations_file
        )

        required_columns = {
            "customer_id",
            "risk_score",
            "risk_category",
            "ltv_band",
            "segment",
            "recommended_action",
        }

        missing_columns = required_columns.difference(
            dataframe.columns
        )

        if missing_columns:
            raise ValueError(
                "Recommendation file is missing required "
                f"columns: {sorted(missing_columns)}"
            )

        dataframe["customer_id"] = (
            dataframe["customer_id"]
            .astype(str)
            .str.strip()
            .str.upper()
        )

        return dataframe

    def _load_rules(self) -> dict[str, Any]:
        if not self.rules_file.exists():
            raise FileNotFoundError(
                f"Recommendation rules not found: "
                f"{self.rules_file}"
            )

        with self.rules_file.open(
                "r",
                encoding="utf-8",
        ) as file:
            return json.load(file)

    def get_recommendation(
            self,
            customer_id: str,
    ) -> dict[str, Any]:

        normalized_customer_id = (
            customer_id.strip().upper()
        )

        if not normalized_customer_id:
            raise ValueError(
                "customer_id is required."
            )

        matches = self.recommendations[
            self.recommendations["customer_id"]
            == normalized_customer_id
            ]

        if matches.empty:
            raise ValueError(
                f"Recommendation not found for customer "
                f"{normalized_customer_id}."
            )

        row = matches.iloc[0]

        return {
            "customer_id": normalized_customer_id,
            "risk_score": float(row["risk_score"]),
            "risk_category": str(
                row["risk_category"]
            ),
            "ltv_band": str(row["ltv_band"]),
            "segment": str(row["segment"]),
            "recommended_action": str(
                row["recommended_action"]
            ),
            "model_version": self.TOOL_VERSION,
        }