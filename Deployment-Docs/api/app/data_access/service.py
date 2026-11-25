import logging
from decimal import Decimal
from pydantic import BaseModel, Field, ValidationError
from api.app.data_access.Controlled_file import DatasetRepository
from api.app.errors import AppException

logger = logging.getLogger("vantage360-ai")


class CustomerRecord(BaseModel):
    customer_id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    age: int = Field(ge=0, le=120)
    gender: str = Field(min_length=1, max_length=20)
    region: str = Field(min_length=1)
    city: str = Field(min_length=1)
    segment: str = Field(min_length=1)
    signup_date: str = Field(min_length=1)
    email: str = Field(min_length=1)
    total_orders: int = Field(ge=0)
    lifetime_value: Decimal = Field(ge=0)


class CustomerService:
    def __init__(self, repository: DatasetRepository) -> None:
        self._repository = repository

    def get_customer_by_id(self, customer_id: str) -> CustomerRecord:
        normalized_customer_id = customer_id.strip().upper()

        customers = self._repository.read_dataset("customers")

        customer = next(
            (
                row
                for row in customers
                if row.get("customer_id", "").strip().upper()
                   == normalized_customer_id
            ),
            None,
        )

        if customer is None:
            raise AppException(
                message="Customer was not found.",
                status_code=404,
            )

        try:
            return CustomerRecord.model_validate(customer)

        except ValidationError as exc:
            logger.warning(
                "Customer record failed validation for customer_id=%s",
                normalized_customer_id,
            )
            raise AppException(
                message="The customer data source contains an invalid record.",
                status_code=503,
            ) from exc

