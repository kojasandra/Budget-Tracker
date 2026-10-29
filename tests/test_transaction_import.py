from datetime import date
from decimal import Decimal

from sqlalchemy import select

from model.category import Category
from model.transaction import Transaction


def test_valid_csv(client, test_session):
    category = Category(name="Other", color="#123456")
    test_session.add(category)
    test_session.commit()

    csv_text = (
        "type,amount,date,description,category\n"
        "expense,12.50,2026-10-08,Lunch,OTHER\n"
        "income,300.00,2026-10-09,,Other\n"
    )
    response = client.post(
        "/transactions/import",
        files={"file": ("transactions.csv", csv_text.encode(), "text/csv")},
    )

    assert response.status_code == 200
    assert response.json() == {"imported": 2, "failed": 0, "errors": []}

    transactions = test_session.scalars(select(Transaction).order_by(Transaction.id)).all()
    assert len(transactions) == 2
    assert transactions[0].type == "expense"
    assert transactions[0].amount == Decimal("12.50")
    assert transactions[0].date == date(2026, 10, 8)
    assert transactions[0].description == "Lunch"
    assert transactions[0].category_id == category.id
    assert transactions[1].type == "income"
    assert transactions[1].amount == Decimal("300.00")
    assert transactions[1].description is None
    assert transactions[1].category_id == category.id


def test_csv_with_valid_and_invalid_rows(client, test_session):
    test_session.add(Category(name="Other", color="#123456"))
    test_session.commit()

    long_description = "x" * 201
    csv_text = (
        "type,amount,date,description,category\n"
        "expense,12.50,2026-10-08,Lunch,Other\n"
        "transfer,10,2026-10-08,Invalid type,Other\n"
        "expense,abc,2026-10-08,Invalid number,Other\n"
        "expense,0,2026-10-08,Zero amount,Other\n"
        "expense,-1,2026-10-08,Negative amount,Other\n"
        "expense,1000000.01,2026-10-08,Over maximum,Other\n"
        "expense,12.345,2026-10-08,Too many decimals,Other\n"
        "expense,10,2026-09-31,Invalid date,Other\n"
        f"expense,10,2026-10-08,{long_description},Other\n"
        "expense,10,2026-10-08,Unknown category,Missing\n"
        ",,,,\n"
        "income,300,2026-10-09,Valid last row,Other\n"
    )
    response = client.post(
        "/transactions/import",
        files={"file": ("transactions.csv", csv_text.encode(), "text/csv")},
    )

    assert response.status_code == 200
    result = response.json()
    assert result["imported"] == 2
    assert result["failed"] == 10
    assert [error["row"] for error in result["errors"]] == list(range(3, 13))

    assert result["errors"][0]["errors"] == ["type: Must be income or expense."]
    assert result["errors"][1]["errors"] == ["amount: Must be a valid number."]
    assert result["errors"][2]["errors"] == ["amount: Must be greater than 0 and at most 1000000."]
    assert result["errors"][3]["errors"] == ["amount: Must be greater than 0 and at most 1000000."]
    assert result["errors"][4]["errors"] == ["amount: Must be greater than 0 and at most 1000000."]
    assert result["errors"][5]["errors"] == ["amount: Must have at most 2 decimal places."]
    assert result["errors"][6]["errors"] == ["date: Must be a valid date in YYYY-MM-DD format."]
    assert result["errors"][7]["errors"] == ["description: Must have at most 200 characters."]
    assert result["errors"][8]["errors"] == ["category: Must already exist."]
    assert result["errors"][9]["errors"] == [
        "type: Field required.",
        "amount: Field required.",
        "date: Field required.",
        "category: Field required.",
        "category: Must already exist.",
    ]

def test_csv_with_wrong_header(client, test_session):
    test_session.add(Category(name="Other", color="#123456"))
    test_session.commit()

    csv_text = "type,amount,date,,"
    response = client.post(
        "/transactions/import",
        files={"file": ("transactions.csv", csv_text.encode(), "text/csv")},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "CSV header must contain type,amount,date,description,category."
    assert test_session.scalars(select(Transaction)).all() == []
