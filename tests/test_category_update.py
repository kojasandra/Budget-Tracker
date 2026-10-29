import pytest

from model.category import Category


@pytest.mark.parametrize("payload, expected_name, expected_color", [
    ({"name": "  Prevoz  "}, "Prevoz", "#123456"),
    ({"color": "#aB12Ef"}, "Hrana", "#aB12Ef"),
    ({"name": "Zabava", "color": "#FFFFFF"}, "Zabava", "#FFFFFF"),
])
def test_update_category_valid(client, test_session, payload, expected_name, expected_color):
    category = Category(name="Hrana", color="#123456")
    test_session.add(category)
    test_session.commit()

    response = client.patch(f"/categories/{category.id}", json=payload)

    assert response.status_code == 200
    assert response.json() == {
        "id": category.id,
        "name": expected_name,
        "color": expected_color,
    }



@pytest.mark.parametrize("payload, error_type", [
    ({"name": ""}, "string_too_short"),
    ({"name": "x" * 31}, "string_too_long"),
    ({"name": 123}, "string_type"),
    ({"color": ""}, "string_too_short"),
    ({"color": "#FFF"}, "string_too_short"),
    ({"color": "#12345678"}, "string_too_long"),
    ({"color": "#GGGGGG"}, "string_pattern_mismatch"),
    ({"color": 1234567}, "string_type"),
])
def test_update_category_invalid_fields(client, test_session, payload, error_type):
    category = Category(name="Hrana", color="#123456")
    test_session.add(category)
    test_session.commit()
    category_id = category.id

    response = client.patch(f"/categories/{category_id}", json=payload)

    assert response.status_code == 422
    error = response.json()["detail"][0]
    assert error["type"] == error_type


@pytest.mark.parametrize("name", ["Prevoz", "Hrana"])
def test_update_category_duplicate_name(client, test_session, name):
    category = Category(name="Hrana", color="#123456")
    test_session.add_all([category, Category(name="Prevoz", color="#FFFFFF")])
    test_session.commit()
    category_id = category.id

    response = client.patch(f"/categories/{category_id}", json={"name": name, "color": "#000000"})

    assert response.status_code == 409
    assert response.json()["detail"] == "A category with this name already exists."


def test_update_category_not_found(client):
    response = client.patch("/categories/999", json={"name": "Hrana"})

    assert response.status_code == 404
    assert response.json()["detail"] == "Category not found."
