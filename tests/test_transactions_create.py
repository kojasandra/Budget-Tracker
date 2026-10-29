from decimal import Decimal

import pytest

from model.category import Category


def test_create_transaction_valid(client, test_session):
    type = "expense"
    amount = "12.50"
    description = "Lunch"
    category = Category(name="Other", color="#123456")
    test_session.add(category)
    test_session.commit()

    response = client.post("/transactions", json={
        "type": type,
        "amount": amount,
        "date": "2026-10-08",
        "description": description,
        "category_id": category.id,
    })

    assert response.status_code == 201
    result = response.json()
    assert result["id"] > 0
    assert result["type"] == type
    assert Decimal(result["amount"]) == Decimal(amount)
    assert result["date"] == "2026-10-08"
    assert result["description"] == description
    assert result["category_id"] == category.id


@pytest.mark.parametrize("payload, error_type", [
    ({"type": 123, "amount": "10", "date": "2026-10-08", "category_id": 1}, "string_type"),
    ({"type": "expense", "amount": "abc", "date": "2026-10-08", "category_id": 1}, "decimal_parsing"),
    ({"type": "expense", "amount": "0", "date": "2026-10-08", "category_id": 1}, "greater_than"),
    ({"type": "expense", "amount": "1000000.01", "date": "2026-10-08", "category_id": 1}, "less_than_equal"),
    ({"type": "expense", "amount": "12.345", "date": "2026-10-08", "category_id": 1}, "decimal_max_places"),
    ({"type": "expense", "amount": "10", "date": "2026-09-31", "category_id": 1}, "date_from_datetime_parsing"),
    ({"type": "expense", "amount": "10", "date": "2026-10-08", "description": "x" * 201, "category_id": 1}, "string_too_long"),
    ({"type": "expense", "amount": "10", "date": "2026-10-08", "category_id": None}, "int_type"),
    ({"type": "expense", "amount": "10", "date": "2026-10-08", "category_id": 0}, "greater_than"),
])
def test_create_transaction_invalid_fields(client, test_session, payload, error_type):
    category = Category(id=1, name="Other", color="#123456")
    test_session.add(category)
    test_session.commit()

    response = client.post("/transactions", json=payload)

    assert response.status_code == 422
    error = response.json()["detail"][0]
    assert error["type"] == error_type


def test_create_transaction_invalid_type(client, test_session):
    type = "transfer"
    category = Category(name="Other", color="#123456")
    test_session.add(category)
    test_session.commit()

    response = client.post("/transactions", json={
        "type": type, "amount": "10", "date": "2026-10-08", "category_id": category.id,
    })

    assert response.status_code == 400
    assert response.json()["detail"] == "Type must be income or expense."


def test_create_transaction_category_not_found(client, test_session):
    response = client.post("/transactions", json={
        "type": "expense", "amount": "10", "date": "2026-10-08", "category_id": 999,
    })

    assert response.status_code == 404
    assert response.json()["detail"] == "Category not found."
