from datetime import date
from decimal import Decimal

from database import Session, engine
from model.base import Base
from model.budget import Budget
from model.category import Category
from model.transaction import Transaction


def create_tables():
    Base.metadata.create_all(engine)


def seed_data():
    with Session() as db:
        category_data = [
            ("Eating out", "#FF5733"),
            ("Other", "#9B59B6"),
            ("Transport", "#3498DB"),
            ("Groceries", "#2ECC71"),
            ("Entertainment", "#F1C40F"),
        ]
        categories = {}
        for name, color in category_data:
            category = Category(name=name, color=color)
            db.add(category)
            db.flush()
            categories[name] = category.id

        transaction_data = [
            ("income", "1500.00", date(2026, 10, 1), "Demo salary", "Other"),
            ("income", "200.00", date(2026, 10, 15), "Demo freelance payment", "Other"),
            ("expense", "12.50", date(2026, 10, 8), "Demo lunch", "Eating out"),
            ("expense", "30.00", date(2026, 10, 8), "Demo dinner", "Eating out"),
            ("expense", "80.00", date(2026, 10, 10), "Demo groceries", "Groceries"),
            ("expense", "70.00", date(2026, 10, 20), "Demo weekly shopping", "Groceries"),
            ("expense", "25.00", date(2026, 10, 31), "Demo bus pass", "Transport"),
            ("expense", "15.00", date(2026, 9, 30), "Demo September lunch", "Eating out"),
        ]
        for type, amount, sent_date, description, category_name in transaction_data:
            category_id = categories[category_name]
            db.add(Transaction(
                type=type,
                amount=Decimal(amount),
                date=sent_date,
                description=description,
                category_id=category_id,
            ))

        budget_data = [
            (date(2026, 10, 1), "Eating out", "100.00"),
            (date(2026, 10, 1), "Groceries", "120.00"),
            (date(2026, 10, 1), "Entertainment", "50.00"),
            (date(2026, 9, 1), "Eating out", "80.00"),
        ]
        for month, category_name, amount in budget_data:
            category_id = categories[category_name]
            db.add(Budget(month=month, category_id=category_id, amount=Decimal(amount)))

        db.commit()


if __name__ == "__main__":
    create_tables()
    seed_data()
    print("Seeding completed successfully.")
