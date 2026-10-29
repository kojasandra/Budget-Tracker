from fastapi import HTTPException
from sqlalchemy import exists, func, select, delete

from database import Session
from model.budget import Budget
from model.category import Category
from model.transaction import Transaction


def check_name(name: str):
    with Session() as db:
        query = select(exists().where(func.lower(Category.name) == name.lower()))
        if db.scalar(query):
            raise HTTPException(status_code=409, detail="A category with this name already exists.")


def get_categories():
    with Session() as db:
        return db.scalars(select(Category).order_by(func.lower(Category.name), Category.id)).all()


def create_category(name: str, color: str):
    with Session() as db:
        check_name(name)
        category = Category(name=name, color=color)
        db.add(category)
        db.commit()
        return category


def update_category(category_id: int, name: str | None = None, color: str | None = None):
    with Session() as db:
        category = db.get(Category, category_id)
        if category is None:
            raise HTTPException(status_code=404, detail="Category not found.")
        if name is not None:
            check_name(name)
            category.name = name
        if color is not None:
            category.color = color
        db.commit()
        return category


def delete_category(category_id: int):
    with Session() as db:
        category = db.get(Category, category_id)
        if category is None:
            raise HTTPException(status_code=404, detail="Category not found.")
        has_transactions = db.scalar(
            select(exists().where(Transaction.category_id == category_id))
        )

        if has_transactions:
            raise HTTPException(
                status_code=409,
                detail="Category with transactions cannot be deleted.",
            )

        db.execute(delete(Budget).where(Budget.category_id == category_id))
        db.delete(category)
        db.commit()
