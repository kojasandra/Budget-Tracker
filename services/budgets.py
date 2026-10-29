from datetime import date
from decimal import Decimal

from fastapi import HTTPException
from sqlalchemy import exists, select

from database import Session
from model.budget import Budget
from model.category import Category


def get_budgets(month: date):
    month = month.replace(day=1)
    with Session() as db:
        return db.scalars(
            select(Budget).where(Budget.month == month).order_by(Budget.category_id)
        ).all()


def create_budget(sent_date: date, category_id: int, amount: Decimal):
    month = sent_date.replace(day=1)
    with Session() as db:
        if db.get(Category, category_id) is None:
            raise HTTPException(status_code=404, detail="Category not found.")
        budget_exists = db.scalar(
            select(exists().where(Budget.category_id == category_id, Budget.month == month))
        )
        if budget_exists:
            raise HTTPException(status_code=409, detail="Budget already exists for this category and month.")
        budget = Budget(month=month, category_id=category_id, amount=amount)
        db.add(budget)
        db.commit()
        return budget


def update_budget(budget_id: int, amount: Decimal):
    with Session() as db:
        budget = db.get(Budget, budget_id)
        if budget is None:
            raise HTTPException(status_code=404, detail="Budget not found.")
        budget.amount = amount
        db.commit()
        return budget


def delete_budget(budget_id: int):
    with Session() as db:
        budget = db.get(Budget, budget_id)
        if budget is None:
            raise HTTPException(status_code=404, detail="Budget not found.")
        db.delete(budget)
        db.commit()
