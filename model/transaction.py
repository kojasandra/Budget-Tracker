from datetime import date as DateType
from decimal import Decimal

from sqlalchemy import CheckConstraint, Date, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(primary_key=True)
    type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )
    amount: Mapped[Decimal] = mapped_column(
        Numeric,
        CheckConstraint("amount > 0 AND amount <= 1000000", name="ck_transactions_amount_range"),
        CheckConstraint("amount = round(amount, 2)", name="ck_transactions_amount_decimals"),
        nullable=False,
    )
    date: Mapped[DateType] = mapped_column(Date, nullable=False)
    description: Mapped[str | None] = mapped_column(String(200), nullable=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"), nullable=False)
