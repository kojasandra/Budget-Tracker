import csv
from datetime import date
from decimal import Decimal, InvalidOperation
from io import TextIOWrapper
from typing import BinaryIO

from fastapi import HTTPException
from sqlalchemy import insert, select

from database import Session
from model.category import Category
from model.transaction import Transaction




def import_transactions(file: BinaryIO):
    text = TextIOWrapper(file, encoding="utf-8-sig", newline="")
    imported = 0
    errors = []
    batch = []

    try:
        reader = csv.DictReader(text, strict=True)
        header = reader.fieldnames
        columns = ["type", "amount", "date", "description", "category"]
        if header is None or len(header) != len(columns) or set(header) != set(columns):
            raise HTTPException(status_code=400, detail="CSV header must contain type,amount,date,description,category.")

        with Session() as db:
            categories = db.scalars(select(Category)).all()
            category_ids = {}
            for category in categories:
                name = category.name.casefold()
                category_ids[name] = category.id

            for row_number, row in enumerate(reader, start=2):
                row_errors = []

                transaction_type = row.get("type")
                if not transaction_type:
                    row_errors.append("type: Field required.")
                elif transaction_type not in ["income", "expense"]:
                    row_errors.append("type: Must be income or expense.")

                amount_value = row.get("amount")
                amount = None
                if not amount_value:
                    row_errors.append("amount: Field required.")
                else:
                    try:
                        amount = Decimal(amount_value)
                    except InvalidOperation:
                        row_errors.append("amount: Must be a valid number.")
                    else:
                        if amount <= 0 or amount > 1000000:
                            row_errors.append("amount: Must be greater than 0 and at most 1000000.")
                        elif amount != amount.quantize(Decimal("0.01")):
                            row_errors.append("amount: Must have at most 2 decimal places.")

                date_value = row.get("date")
                transaction_date = None
                if not date_value:
                    row_errors.append("date: Field required.")
                else:
                    try:
                        transaction_date = date.fromisoformat(date_value)
                    except ValueError:
                        row_errors.append("date: Must be a valid date in YYYY-MM-DD format.")

                description = row.get("description") or None
                if description is not None and len(description) > 200:
                    row_errors.append("description: Must have at most 200 characters.")

                category_name = (row.get("category") or "").strip().casefold()
                if not category_name:
                    row_errors.append("category: Field required.")
                category_id = category_ids.get(category_name)
                if category_id is None:
                    row_errors.append("category: Must already exist.")

                if row_errors:
                    errors.append({"row": row_number, "errors": row_errors})
                    continue

                batch.append({
                    "type": transaction_type,
                    "amount": amount,
                    "date": transaction_date,
                    "description": description,
                    "category_id": category_id,
                })
                # Saving data in batches
                if len(batch) == 1000:
                    db.execute(insert(Transaction), batch)
                    imported += 1000
                    batch = []

            # Saving remaining data
            if batch:
                db.execute(insert(Transaction), batch)
                imported += len(batch)
            db.commit()

    except (UnicodeDecodeError, csv.Error) as exc:
        raise HTTPException(status_code=400, detail="Invalid CSV. Nothing imported.") from exc

    return {"imported": imported, "failed": len(errors), "errors": errors}
