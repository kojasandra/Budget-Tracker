from datetime import date
from decimal import Decimal

from model.category import Category
from model.transaction import Transaction


def test_empty_month(client):
    response = client.get("/summary?year=2026&month=10")

    assert response.status_code == 200
    result = response.json()
    assert Decimal(result["total_income"]) == 0
    assert Decimal(result["total_expense"]) == 0
    assert Decimal(result["balance"]) == 0


def test_month_with_transactions(client, test_session):
    category = Category(name="Other", color="#123456")
    test_session.add(category)
    test_session.flush()

    test_session.add_all([
        Transaction(
            type="income",
            amount=Decimal("1000.00"),
            date=date(2026, 10, 1),
            category_id=category.id,
        ),
        Transaction(
            type="expense",
            amount=Decimal("300.50"),
            date=date(2026, 10, 15),
            category_id=category.id,
        ),
        Transaction(
            type="expense",
            amount=Decimal("800.00"),
            date=date(2026, 10, 31),
            category_id=category.id,
        ),
        Transaction(
            type="income",
            amount=Decimal("5000.00"),
            date=date(2026, 11, 1),
            category_id=category.id,
        ),
    ])
    test_session.commit()

    response = client.get("/summary?year=2026&month=10")

    assert response.status_code == 200
    result = response.json()
    assert Decimal(result["total_income"]) == Decimal("1000.00")
    assert Decimal(result["total_expense"]) == Decimal("1100.50")
    assert Decimal(result["balance"]) == Decimal("-100.50")
