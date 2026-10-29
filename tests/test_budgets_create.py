from datetime import date
from decimal import Decimal

import pytest

from model.budget import Budget
from model.category import Category


def test_create_budget_valid(client, test_session):

    category = Category(name="Hrana", color="#123456")
    test_session.add(category)
    test_session.commit()

    amount = 25000.50

    response = client.post("/budgets", json={
        "month": "2026-10-27",
        "category_id": category.id,
        "amount": amount,
    })

    assert response.status_code == 201
    result = response.json()
    assert result["id"] > 0
    assert result["month"] == "2026-10-01"
    assert result["category_id"] == category.id
    assert Decimal(result["amount"]) == Decimal(amount)


@pytest.mark.parametrize("payload, error_type", [
    ({"month": None, "category_id": 1, "amount": "100"}, "date_type"),
    ({"month": "", "category_id": 1, "amount": "100"}, "date_from_datetime_parsing"),
    ({"month": "2026-09-31", "category_id": 1, "amount": "100"}, "date_from_datetime_parsing"),
    ({"month": "2026-10-01", "category_id": None, "amount": "100"}, "int_type"),
    ({"month": "2026-10-01", "category_id": -1, "amount": "100"}, "greater_than"),
    ({"month": "2026-10-01", "category_id": "abc", "amount": "100"}, "int_parsing"),
    ({"month": "2026-10-01", "category_id": 1, "amount": "abc"}, "decimal_parsing"),
    ({"month": "2026-10-01", "category_id": 1, "amount": "0"}, "greater_than"),
    ({"month": "2026-10-01", "category_id": 1, "amount": "-1"}, "greater_than"),
    ({"month": "2026-10-01", "category_id": 1, "amount": "1000000.01"}, "less_than_equal"),
    ({"month": "2026-10-01", "category_id": 1, "amount": "12.345"}, "decimal_max_places"),
])
def test_create_budget_invalid_fields(client, test_session, payload, error_type):
    category = Category(id=1, name="Hrana", color="#123456")
    test_session.add(category)
    test_session.commit()

    response = client.post("/budgets", json=payload)

    assert response.status_code == 422
    error = response.json()["detail"][0]
    assert error["type"] == error_type

def test_create_budget_category_not_found(client, test_session):
    response = client.post("/budgets", json={
        "month": "2026-10-01", "category_id": 999, "amount": "100",
    })

    assert response.status_code == 404
    assert response.json()["detail"] == "Category not found."


def test_create_budget_duplicate(client, test_session):
    category = Category(name="Hrana", color="#123456")
    test_session.add(category)
    test_session.flush()
    test_session.add(Budget(month=date(2026, 10, 1), category_id=category.id, amount=Decimal("100")))
    test_session.commit()

    response = client.post("/budgets", json={
        "month": "2026-10-27", "category_id": category.id, "amount": "200",
    })

    assert response.status_code == 409
    assert response.json()["detail"] == "Budget already exists for this category and month."
