from datetime import date
from decimal import Decimal

import pytest

from model.budget import Budget
from model.category import Category
from model.transaction import Transaction


def test_category_summary_empty_month(client):
    response = client.get("/summary/categories?year=2026&month=10")

    assert response.status_code == 200
    assert response.json() == []


def test_category_summary_month_boundaries_and_expense_total(client, test_session):
    category = Category(name="Hrana", color="#123456")
    test_session.add(category)
    test_session.flush()
    test_session.add_all([
        Transaction(type="expense", amount=Decimal("20.25"), date=date(2026, 10, 1), category_id=category.id),
        Transaction(type="expense", amount=Decimal("30.50"), date=date(2026, 10, 31), category_id=category.id),
        Transaction(type="income", amount=Decimal("500"), date=date(2026, 10, 15), category_id=category.id),
        Transaction(type="expense", amount=Decimal("900"), date=date(2026, 9, 30), category_id=category.id),
        Transaction(type="expense", amount=Decimal("800"), date=date(2026, 11, 1), category_id=category.id),
        Transaction(type="expense", amount=Decimal("700"), date=date(2025, 10, 8), category_id=category.id),
        Budget(month=date(2026, 10, 1), amount=Decimal("100"), category_id=category.id),
        Budget(month=date(2026, 9, 1), amount=Decimal("1000"), category_id=category.id),
        Budget(month=date(2026, 11, 1), amount=Decimal("2000"), category_id=category.id),
        Budget(month=date(2025, 10, 1), amount=Decimal("3000"), category_id=category.id),
    ])
    test_session.commit()

    response = client.get("/summary/categories?year=2026&month=10")

    assert response.status_code == 200
    result = response.json()
    assert len(result) == 1
    assert Decimal(result[0]["spent"]) == Decimal("50.75")
    assert Decimal(result[0]["budget"]) == Decimal("100")
    assert Decimal(result[0]["remaining"]) == Decimal("49.25")


def test_category_summary_sorted_by_expense_then_name(client, test_session):
    food = Category(name="Hrana", color="#123456")
    transport = Category(name="Prevoz", color="#FFFFFF")
    car = Category(name="auto", color="#000000")
    entertainment = Category(name="Zabava", color="#ABCDEF")
    test_session.add_all([food, transport, car, entertainment])
    test_session.flush()
    test_session.add_all([
        Transaction(type="expense", amount=Decimal("100"), date=date(2026, 10, 8), category_id=food.id),
        Transaction(type="expense", amount=Decimal("200"), date=date(2026, 10, 8), category_id=transport.id),
        Transaction(type="expense", amount=Decimal("100"), date=date(2026, 10, 8), category_id=car.id),
        Budget(month=date(2026, 10, 1), amount=Decimal("500"), category_id=entertainment.id),
    ])
    test_session.commit()

    response = client.get("/summary/categories?year=2026&month=10")

    assert response.status_code == 200
    result = response.json()
    assert [category["name"] for category in result] == ["Prevoz", "auto", "Hrana", "Zabava"]
    assert [Decimal(category["spent"]) for category in result] == [200, 100, 100, 0]


@pytest.mark.parametrize("params", [
    {"year": 2026},
    {"month": 10},
    {"year": 2026, "month": 0},
])
def test_category_summary_invalid_parameters(client, params):
    response = client.get("/summary/categories", params=params)

    assert response.status_code == 422
