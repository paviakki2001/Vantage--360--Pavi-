import json
import logging
from pathlib import Path
from typing import Any

import pandas as pd


logger = logging.getLogger("vantage360-ai")


class ForecastService:
    TOOL_NAME = "revenue_forecast"
    TOOL_VERSION = "v1"

    def __init__(self):
        project_root = Path(__file__).resolve().parents[3]

        self.metadata_file = (
                project_root
                / "models"
                / "artifact"
                / "revenue_forecast_metadata.json"
        )

        self.forecast_file = (
                project_root
                / "models"
                / "artifact"
                / "revenue_forecast_next3months.csv"
        )

        self.model_file = (
                project_root
                / "models"
                / "trained_models"
                / "revenue_forecast_prophet_v1.pkl"
        )

        self.metadata = self._load_metadata()
        self.forecast_data = self._load_forecast()

    def _load_metadata(self) -> dict[str, Any]:
        if not self.metadata_file.exists():
            raise FileNotFoundError(
                f"Forecast metadata not found: {self.metadata_file}"
            )

        with self.metadata_file.open(
                "r",
                encoding="utf-8",
        ) as file:
            return json.load(file)

    def _load_forecast(self) -> pd.DataFrame:
        if not self.forecast_file.exists():
            raise FileNotFoundError(
                f"Forecast file not found: {self.forecast_file}"
            )

        dataframe = pd.read_csv(self.forecast_file)

        required_columns = {
            "ds",
            "yhat",
            "yhat_lower",
            "yhat_upper",
        }

        missing_columns = required_columns.difference(
            dataframe.columns
        )

        if missing_columns:
            raise ValueError(
                "Forecast file is missing required columns: "
                f"{sorted(missing_columns)}"
            )

        dataframe["ds"] = pd.to_datetime(
            dataframe["ds"]
        )

        return dataframe

    def get_forecast(self) -> dict[str, Any]:

        forecast = []

        for _, row in self.forecast_data.iterrows():

            forecast.append(
                {
                    "date": row["ds"].strftime("%Y-%m-%d"),
                    "predicted_revenue": float(row["yhat"]),
                    "lower_bound": float(row["yhat_lower"]),
                    "upper_bound": float(row["yhat_upper"]),
                }
            )

        return {
            "model_version": self.metadata.get(
                "model_version",
                "unknown",
            ),
            "training_period": self.metadata.get(
                "training_period"
            ),
            "forecast_horizon": len(forecast),
            "forecast": forecast,
        }