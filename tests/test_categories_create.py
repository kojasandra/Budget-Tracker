import pytest

from model.category import Category


def test_create_category_valid(client, test_session):
    response = client.post("/categories", json={"name": "  Hrana  ", "color": "#aB12Ef"})

    assert response.status_code == 201
    result = response.json()
    assert result["id"] > 0
    assert result["name"] == "Hrana"
    assert result["color"] == "#aB12Ef"

    category = test_session.get(Category, result["id"])
    assert category is not None
    assert category.name == "Hrana"
    assert category.color == "#aB12Ef"


@pytest.mark.parametrize("payload, error_type", [
    ({"color": "#123456"}, "missing"),
    ({"name": None, "color": "#123456"}, "string_type"),
    ({"name": "", "color": "#123456"}, "string_too_short"),
    ({"name": "x" * 31, "color": "#123456"}, "string_too_long"),
    ({"name": 123, "color": "#123456"}, "string_type"),
    ({"name": "Hrana"}, "missing"),
    ({"name": "Hrana", "color": None}, "string_type"),
    ({"name": "Hrana", "color": ""}, "string_too_short"),
    ({"name": "Hrana", "color": "#FFF"}, "string_too_short"),
    ({"name": "Hrana", "color": "#12345678"}, "string_too_long"),
    ({"name": "Hrana", "color": "#12 456"}, "string_pattern_mismatch"),
])
def test_create_category_invalid_fields(client, test_session, payload, error_type):
    response = client.post("/categories", json=payload)

    assert response.status_code == 422
    error = response.json()["detail"][0]
    assert error["type"] == error_type


def test_create_category_duplicate(client, test_session):
    test_session.add(Category(name="Hrana", color="#123456"))
    test_session.commit()

    response = client.post("/categories", json={"name": "Hrana", "color": "#FFFFFF"})

    assert response.status_code == 409
    assert response.json()["detail"] == "A category with this name already exists."
