from typing import Any

from pydantic import BaseModel, Field


class CustomerModelRequest(BaseModel):
    customer_id: str = Field(
        ...,
        min_length=1,
        description="Unique customer identifier.",
        examples=["CUST00001"],
    )


class ForecastRequest(BaseModel):

    pass


class StandardModelResponse(BaseModel):
    tool: str
    version: str
    input: dict[str, Any]
    output: dict[str, Any]
    status: str
    timestamp: str
    metadata: dict[str, Any] = Field(
        default_factory=dict
    )
