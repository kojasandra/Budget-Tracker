from datetime import date as DateType
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class TransactionCreate(BaseModel):
    type: str
    amount: Decimal = Field(gt=0, le=1000000, decimal_places=2)
    date: DateType
    description: str | None = Field(default=None, max_length=200)
    category_id: int = Field(gt=0)


class TransactionUpdate(BaseModel):
    type: str | None = None
    amount: Decimal | None = Field(default=None, gt=0, le=1000000, decimal_places=2)
    date: DateType | None = None
    description: str | None = Field(default=None, max_length=200)
    category_id: int | None = Field(default=None, gt=0)


class TransactionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    type: str
    amount: Decimal
    date: DateType
    description: str | None
    category_id: int


class TransactionListResponse(BaseModel):
    items: list[TransactionResponse]
    total: int
    page: int
    page_size: int
