from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class BudgetCreate(BaseModel):
    month: date
    category_id: int = Field(gt=0)
    amount: Decimal = Field(gt=0, le=1000000, decimal_places=2)

class BudgetUpdate(BaseModel):
    amount: Decimal = Field(gt=0, le=1000000, decimal_places=2)


class BudgetResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    month: date
    category_id: int
    amount: Decimal
