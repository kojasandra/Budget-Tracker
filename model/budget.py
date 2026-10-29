from datetime import date
from decimal import Decimal

from sqlalchemy import CheckConstraint, Date, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class Budget(Base):
    __tablename__ = "budgets"

    id: Mapped[int] = mapped_column(primary_key=True)
    month: Mapped[date] = mapped_column(Date, nullable=False)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id", ondelete="CASCADE"), nullable=False)
    amount: Mapped[Decimal] = mapped_column(
        Numeric,
        CheckConstraint("amount > 0 AND amount <= 1000000", name="ck_budgets_amount_range"),
        CheckConstraint("amount = round(amount, 2)", name="ck_budgets_amount_decimals"),
        nullable=False,
    )
