import json
import logging
from pathlib import Path

import joblib
import pandas as pd

from api.app.data_access.Controlled_file import DatasetRepository
from api.app.data_access.service import CustomerService
from api.app.errors import AppException
from api.app.config import settings

from api.app.cache.cache_query import QueryCache
import time

logger = logging.getLogger("vantage360-ai")


class ChurnService:

    TOOL_NAME = "churn_risk"
    TOOL_VERSION = "v2"
    MODEL_VERSION = "rf-v2-official-proxy"

    def __init__(self, repository: DatasetRepository):
        self.repository = repository
        self.customer_service = CustomerService(repository)

        # Project root
        project_root = Path(__file__).resolve().parents[3]

        # V2 model artifacts
        self.feature_file = (
                project_root
                / "models"
                / "artifact"
                / "churn_rf_v2_features.json"
        )

        self.model_file = (
                project_root
                / "models"
                / "trained_models"
                / "churn_rf_v2.pkl"
        )

        # Official feature dataset
        self.customer_features_file = (
                Path(settings.master_data_directory)
                / "customer_features.csv"
        )

        # Load feature definition
        self.features = self.load_features()

        # Load Random Forest
        self.model = self.load_model()

        # Load official customer feature data
        self.customer_features = self.load_customer_features()

        # adding the cache for 5min, so if there is any updated version the cache won't keep the old one
        self.cache = QueryCache(ttl_seconds=300)

        logger.info(
                "ChurnService initialized: model_version=%s features=%s",
                self.MODEL_VERSION,
                self.features,
            )

    def load_features(self):
        """Load the official V2 feature columns."""

        if not self.feature_file.exists():
            raise AppException(
                message="Churn V2 feature definition was not found.",
                status_code=500,
            )

        try:
            with open(self.feature_file, "r", encoding="utf-8") as file:
                data = json.load(file)

            features = data["feature_cols"]

            if not features:
                raise ValueError("Feature list is empty.")

            return features

        except (OSError, json.JSONDecodeError, KeyError, ValueError) as exc:
            logger.exception("Failed to load churn V2 feature definition.")
            raise AppException(
                message="Failed to load churn V2 feature definition.",
                status_code=500,
            ) from exc

    def load_model(self):
        """Load the official V2 Random Forest model."""

        if not self.model_file.exists():
            raise AppException(
                message="Churn V2 model was not found.",
                status_code=500,
            )

        try:
            return joblib.load(self.model_file)

        except Exception as exc:
            logger.exception("Failed to load churn V2 model.")
            raise AppException(
                message="Failed to load churn V2 model.",
                status_code=500,
            ) from exc

    def load_customer_features(self):
        """Load the official ML feature dataset."""

        if not self.customer_features_file.exists():
            raise AppException(
                message="Official customer feature dataset was not found.",
                status_code=500,
            )

        try:
            dataframe = pd.read_csv(self.customer_features_file)

        except Exception as exc:
            logger.exception(
                "Failed to load customer_features.csv."
            )
            raise AppException(
                message="Failed to load the official customer feature dataset.",
                status_code=500,
            ) from exc

        required_columns = ["customer_id", *self.features]

        missing_columns = [
            column
            for column in required_columns
            if column not in dataframe.columns
        ]

        if missing_columns:
            logger.error(
                "Missing churn feature columns: %s",
                missing_columns,
            )

            raise AppException(
                message=(
                    "The official customer feature dataset is missing "
                    "required churn features."
                ),
                status_code=500,
            )

        return dataframe

    def get_customer_features(self, customer_id: str):
        """Retrieve the official V2 feature row for a customer."""

        normalized_customer_id = customer_id.strip().upper()

        matches = self.customer_features[
            self.customer_features["customer_id"]
            .astype(str)
            .str.strip()
            .str.upper()
            == normalized_customer_id
            ]

        if matches.empty:
            raise AppException(
                message="Customer features were not found.",
                status_code=404,
            )

        return matches.iloc[0]

    def predict(self, customer_id: str, correlation_id: str | None = None,):

        normalized_customer_id = customer_id.strip().upper()

        if not normalized_customer_id:
            raise AppException(
                message="customer_id is required.",
                status_code=400,
            )

        # check query cache
        cache_key = f"{self.TOOL_NAME}:{normalized_customer_id}"

        cached_result = self.cache.get(cache_key)

        if cached_result is not None:
            logger.info(
                "churn_tool_execution "
                "correlation_id=%s customer_id=%s execution_time_ms=%.2f",
                correlation_id,
                normalized_customer_id,
            )
            return cached_result

        logger.info(
            "Churn prediction cache miss for customer_id=%s",
            normalized_customer_id,
        )

        # Make sure the customer exists
        self.customer_service.get_customer_by_id(
            normalized_customer_id
        )

        # Get official ML features
        customer_features = self.get_customer_features(
            normalized_customer_id
        )

        try:
            # Preserve the exact feature order from the artifact
            values = [
                float(customer_features[feature])
                for feature in self.features
            ]

        except (TypeError, ValueError, KeyError) as exc:
            logger.exception(
                "Invalid churn feature values for customer_id=%s",
                normalized_customer_id,
            )

            raise AppException(
                message="Invalid churn feature values.",
                status_code=422,
            ) from exc

        # Random Forest does NOT require scaling
        prediction_input = pd.DataFrame(
            [values],
            columns=self.features,
        )

        tool_start_time = time.perf_counter()

        try:
            prediction = self.model.predict(
                prediction_input
            )[0]

            probabilities = self.model.predict_proba(
                prediction_input
            )[0]

        except Exception as exc:
            logger.exception(
                "Churn model prediction failed for customer_id=%s",
                normalized_customer_id,
            )

            raise AppException(
                message="Churn model prediction failed.",
                status_code=500,
            ) from exc



        tool_execution_time_ms = (
            time.perf_counter() - tool_start_time
            ) * 1000

        logger.info(
            "churn_tool_execution "
            "customer_id=%s "
            "correlation_id=%s execution_time_ms=%.2f",
            correlation_id,
            normalized_customer_id,
            tool_execution_time_ms,
        )

        # Find probability of the positive/churn class
        classes = list(self.model.classes_)

        if 1 in classes:
            churn_probability = probabilities[
                classes.index(1)
            ]
        else:
            churn_probability = probabilities[-1]

        risk_score = round(
            float(churn_probability),
            6,
        )

        # Risk classification
        if risk_score >= 0.7:
            risk_category = "High"
        elif risk_score >= 0.4:
            risk_category = "Medium"
        else:
            risk_category = "Low"

        # Official Data Analyst proxy
        official_proxy = None

        if "attrition_risk_proxy" in customer_features.index:
            official_proxy = customer_features[
                "attrition_risk_proxy"
            ]

            if pd.isna(official_proxy):
                official_proxy = None
            else:
                official_proxy = str(official_proxy)

        result = {
            "prediction": str(prediction),
            "risk_score": risk_score,
            "risk_category": risk_category,
            "official_proxy": official_proxy,
            "model_version": self.MODEL_VERSION,
        }

        self.cache.set(cache_key, result)

        logger.info(
            "Churn prediction cached for customer_id=%s",
            normalized_customer_id,
        )

        return result

