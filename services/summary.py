from calendar import monthrange
from datetime import date
from decimal import Decimal

from sqlalchemy import func, select

from database import Session
from model.budget import Budget
from model.category import Category
from model.transaction import Transaction


def get_monthly_summary(year: int, month: int):
    first_day = date(year, month, 1)
    last_day = date(year, month, monthrange(year, month)[1])

    with Session() as db:
        total_income = db.scalar(
            select(func.sum(Transaction.amount))
            .where(
                Transaction.type == "income",
                Transaction.date >= first_day,
                Transaction.date <= last_day,
            )
        )
        if total_income is None:
            total_income = Decimal("0")

        total_expense = db.scalar(
            select(func.sum(Transaction.amount))
            .where(
                Transaction.type == "expense",
                Transaction.date >= first_day,
                Transaction.date <= last_day,
            )
        )
        if total_expense is None:
            total_expense = Decimal("0")

        return {
            "total_income": total_income,
            "total_expense": total_expense,
            "balance": total_income - total_expense,
        }


def get_category_summary(year: int, month: int):
    first_day = date(year, month, 1)
    last_day = date(year, month, monthrange(year, month)[1])

    with Session() as db:
        categories = db.scalars(select(Category)).all()
        summary = []

        for category in categories:
            spent = db.scalar(
                select(func.sum(Transaction.amount))
                .where(
                    Transaction.category_id == category.id,
                    Transaction.type == "expense",
                    Transaction.date >= first_day,
                    Transaction.date <= last_day,
                )
            )
            budget = db.scalar(
                select(func.sum(Budget.amount))
                .where(
                    Budget.category_id == category.id,
                    Budget.month >= first_day,
                    Budget.month <= last_day,
                )
            )

            if spent is None and budget is None:
                continue
            if spent is None:
                spent = Decimal("0")
            if budget is None:
                budget = Decimal("0")

            summary.append({
                "id": category.id,
                "name": category.name,
                "spent": spent,
                "budget": budget,
                "remaining": budget - spent,
            })

        summary.sort(key=lambda category: category["name"].lower())
        summary.sort(key=lambda category: category["spent"], reverse=True)
        return summary
