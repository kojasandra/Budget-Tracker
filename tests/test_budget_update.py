from datetime import date
from decimal import Decimal

import pytest

from model.budget import Budget
from model.category import Category


def test_update_budget_valid(client, test_session):
    category = Category(name="Hrana", color="#123456")
    test_session.add(category)
    test_session.flush()
    budget = Budget(month=date(2026, 10, 1), category_id=category.id, amount=Decimal("100"))
    test_session.add(budget)
    test_session.commit()
    budget_id = budget.id
    category_id = category.id
    new_value = "1000000.00"
    response = client.patch(f"/budgets/{budget_id}", json={"amount": new_value})

    assert response.status_code == 200
    result = response.json()
    assert result["id"] == budget_id
    assert result["month"] == "2026-10-01"
    assert result["category_id"] == category_id
    assert Decimal(result["amount"]) == Decimal(new_value)

    test_session.expire_all()
    saved_budget = test_session.get(Budget, budget_id)
    assert saved_budget.amount == Decimal(new_value)
    assert saved_budget.month == date(2026, 10, 1)
    assert saved_budget.category_id == category_id


@pytest.mark.parametrize("payload, error_type", [
    ({}, "missing"),
    ({"amount": None}, "decimal_type"),
    ({"amount": ""}, "decimal_parsing"),
    ({"amount": "abc"}, "decimal_parsing"),
    ({"amount": "0"}, "greater_than"),
    ({"amount": "1000000.01"}, "less_than_equal"),
    ({"amount": "12.345"}, "decimal_max_places"),
])
def test_update_budget_invalid_amount(client, test_session, payload, error_type):
    category = Category(name="Hrana", color="#123456")
    test_session.add(category)
    test_session.flush()
    budget = Budget(month=date(2026, 10, 1), category_id=category.id, amount=Decimal("100"))
    test_session.add(budget)
    test_session.commit()
    budget_id = budget.id

    response = client.patch(f"/budgets/{budget_id}", json=payload)

    assert response.status_code == 422
    error = response.json()["detail"][0]
    assert error["type"] == error_type


def test_update_budget_not_found(client):
    response = client.patch("/budgets/999", json={"amount": "200"})

    assert response.status_code == 404
    assert response.json()["detail"] == "Budget not found."
