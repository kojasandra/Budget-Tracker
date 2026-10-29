from datetime import date
from decimal import Decimal

import pytest

from model.category import Category
from model.transaction import Transaction


def create_test_transaction(test_session):
    category = Category(name="Other", color="#123456")
    test_session.add(category)
    test_session.flush()
    transaction = Transaction(
        type="expense", amount=Decimal("100"), date=date(2026, 10, 8),
        description="Lunch", category_id=category.id,
    )
    test_session.add(transaction)
    test_session.commit()
    return transaction


@pytest.mark.parametrize("payload", [
    {"type": "income"},
    {"amount": "0.01"},
    {"amount": "250.50"},
    {"amount": "1000000.00"},
    {"date": "2024-02-29"},
    {"description": "Updated description"},
    {"description": ""},
    {"description": "x" * 200},
    {"type": "income", "amount": "300", "date": "2026-11-01", "description": "Salary"},
])
def test_update_transaction_valid(client, test_session, payload):
    transaction = create_test_transaction(test_session)
    transaction_id = transaction.id
    category_id = transaction.category_id

    response = client.patch(f"/transactions/{transaction_id}", json=payload)

    assert response.status_code == 200
    result = response.json()
    assert result["id"] == transaction_id
    assert result["type"] == payload.get("type", "expense")
    assert Decimal(result["amount"]) == Decimal(payload.get("amount", "100"))
    assert result["date"] == payload.get("date", "2026-10-08")
    assert result["description"] == payload.get("description", "Lunch")
    assert result["category_id"] == category_id


def test_update_transaction_category(client, test_session):
    transaction = create_test_transaction(test_session)
    category = Category(name="Salary", color="#FFFFFF")
    test_session.add(category)
    test_session.commit()
    transaction_id = transaction.id
    category_id = category.id

    response = client.patch(f"/transactions/{transaction_id}", json={"category_id": category_id})

    assert response.status_code == 200
    assert response.json()["category_id"] == category_id



@pytest.mark.parametrize("payload, error_type", [
    ({"type": 123}, "string_type"),
    ({"amount": "abc"}, "decimal_parsing"),
    ({"amount": "0"}, "greater_than"),
    ({"amount": "1000000.01"}, "less_than_equal"),
    ({"amount": "12.345"}, "decimal_max_places"),
    ({"date": "2026-09-31"}, "date_from_datetime_parsing"),
    ({"description": "x" * 201}, "string_too_long"),
    ({"description": 123}, "string_type"),
    ({"category_id": 0}, "greater_than"),
    ({"category_id": "abc"}, "int_parsing"),
])
def test_update_transaction_invalid_fields(client, test_session, payload, error_type):
    transaction = create_test_transaction(test_session)
    transaction_id = transaction.id

    response = client.patch(f"/transactions/{transaction_id}", json=payload)

    assert response.status_code == 422
    error = response.json()["detail"][0]
    assert error["type"] == error_type



def test_update_transaction_invalid_type(client, test_session):
    type = "transfer"
    transaction = create_test_transaction(test_session)
    transaction_id = transaction.id

    response = client.patch(f"/transactions/{transaction_id}", json={"type": type, "amount": "200"})

    assert response.status_code == 400
    assert response.json()["detail"] == "Type must be income or expense."



def test_update_transaction_category_not_found(client, test_session):
    transaction = create_test_transaction(test_session)
    transaction_id = transaction.id

    response = client.patch(f"/transactions/{transaction_id}", json={"category_id": 999, "amount": "200"})

    assert response.status_code == 404
    assert response.json()["detail"] == "Category not found."


def test_update_transaction_not_found(client):
    response = client.patch("/transactions/999", json={"amount": "200"})

    assert response.status_code == 404
    assert response.json()["detail"] == "Transaction not found."
