from datetime import date
from decimal import Decimal

from fastapi import HTTPException
from sqlalchemy import func, select

from database import Session
from model.category import Category
from model.transaction import Transaction


def get_transactions(
    page: int = 1,
    page_size: int = 20,
    date_from: date | None = None,
    date_to: date | None = None,
    category_id: int | None = None,
    type: str | None = None,
    description: str | None = None,
):
    if date_from is not None and date_to is not None and date_from > date_to:
        raise HTTPException(status_code=400, detail="date_from must be before or equal to date_to.")
    if type is not None and type not in ["income", "expense"]:
        raise HTTPException(status_code=400, detail="Type must be income or expense.")

    with Session() as db:
        query = select(Transaction)
        if date_from is not None:
            query = query.where(Transaction.date >= date_from)
        if date_to is not None:
            query = query.where(Transaction.date <= date_to)
        if category_id is not None:
            query = query.where(Transaction.category_id == category_id)
        if type is not None:
            query = query.where(Transaction.type == type)
        if description is not None:
            query = query.where(Transaction.description.icontains(description, autoescape=True))

        total = db.scalar(select(func.count()).select_from(query.subquery()))
        query = query.order_by(Transaction.date.desc(), Transaction.id.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)
        transactions = db.scalars(query).all()
        return {"items": transactions, "total": total, "page": page, "page_size": page_size}


def create_transaction(type: str, amount: Decimal, sent_date: date, category_id: int, description: str | None = None):
    if type not in ["income", "expense"]:
        raise HTTPException(status_code=400, detail="Type must be income or expense.")
    with Session() as db:
        if db.get(Category, category_id) is None:
            raise HTTPException(status_code=404, detail="Category not found.")
        transaction = Transaction(
            type=type,
            amount=amount,
            date=sent_date,
            description=description,
            category_id=category_id,
        )
        db.add(transaction)
        db.commit()
        return transaction


def get_transaction(transaction_id: int):
    with Session() as db:
        transaction = db.get(Transaction, transaction_id)
        if transaction is None:
            raise HTTPException(status_code=404, detail="Transaction not found.")
        return transaction


def update_transaction(
    transaction_id: int,
    type: str | None = None,
    amount: Decimal | None = None,
    sent_date: date | None = None,
    category_id: int | None = None,
    description: str | None = None,
):
    with Session() as db:
        transaction = db.get(Transaction, transaction_id)
        if transaction is None:
            raise HTTPException(status_code=404, detail="Transaction not found.")
        if category_id is not None:
            if db.get(Category, category_id) is None:
                raise HTTPException(status_code=404, detail="Category not found.")
            transaction.category_id = category_id
        if type is not None:
            if type not in ["income", "expense"]:
                raise HTTPException(status_code=400, detail="Type must be income or expense.")
            transaction.type = type
        if amount is not None:
            transaction.amount = amount
        if sent_date is not None:
            transaction.date = sent_date
        if description is not None:
            transaction.description = description
        db.commit()
        return transaction


def delete_transaction(transaction_id: int):
    with Session() as db:
        transaction = db.get(Transaction, transaction_id)
        if transaction is None:
            raise HTTPException(status_code=404, detail="Transaction not found.")
        db.delete(transaction)
        db.commit()
