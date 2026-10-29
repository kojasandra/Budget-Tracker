from decimal import Decimal

from pydantic import BaseModel


class MonthlySummary(BaseModel):
    total_income: Decimal
    total_expense: Decimal
    balance: Decimal


class CategorySummary(BaseModel):
    id: int
    name: str
    spent: Decimal
    budget: Decimal
    remaining: Decimal
