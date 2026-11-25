import csv
import logging
from pathlib import Path
from typing import Final

from api.app.errors import AppException

logger = logging.getLogger("vantage360-ai")

class DatasetRepository:

    _ALLOWED_DATASETS: Final[dict[str, str]] = {
        "customers": "customers.csv",
        "products": "products.csv",
        "transactions": "transactions.csv",
        "customer_support": "customer_support.csv",
        "marketing_campaigns": "marketing_campaigns.csv",
    }

    def __init__(self, master_data_directory: Path) -> None:
        self._master_data_directory = master_data_directory.resolve()
    def read_dataset(self, dataset_name: str) -> list[dict[str, str]]:

        filename = self._ALLOWED_DATASETS.get(dataset_name)

        if filename is None:
            raise AppException(
                message="Access to the requested dataset is not permitted.",
                status_code=403,
            )

        dataset_path = (
                self._master_data_directory / filename
        ).resolve()

        if dataset_path.parent != self._master_data_directory:
            logger.error("Blocked an invalid dataset path.")
            raise AppException(
                message="Access to the requested dataset is not permitted.",
                status_code=403,
            )

        if not dataset_path.is_file():
            logger.error(
                "Configured development dataset is unavailable: %s",
                dataset_name,
            )
            raise AppException(
                message="The development data source is temporarily unavailable.",
                status_code=503,
            )

        try:
            with dataset_path.open(
                    mode="r",
                    encoding="utf-8-sig",
                    newline="",
            ) as dataset_file:
                return list(csv.DictReader(dataset_file))

        except (OSError, csv.Error) as exc:
            logger.exception(
                "Unable to read development dataset: %s",
                dataset_name,
            )
            raise AppException(
                message="The development data source is temporarily unavailable.",
                status_code=503,
            ) from exc
