from datetime import date

from fastapi import APIRouter, Query, Response

from schemas.transactions import TransactionCreate, TransactionListResponse, TransactionResponse, TransactionUpdate
from services.transactions import create_transaction, delete_transaction, get_transaction, get_transactions, update_transaction


router = APIRouter(tags=["transactions"])


@router.get("/transactions", response_model=TransactionListResponse)
def get_transactions_api(
    page: int = Query(default=1, gt=0),
    page_size: int = Query(default=10, gt=0),
    date_from: date | None = None,
    date_to: date | None = None,
    category_id: int | None = Query(default=None, gt=0),
    type: str | None = None,
    description: str | None = None,
):
    return get_transactions(
        page=page,
        page_size=page_size,
        date_from=date_from,
        date_to=date_to,
        category_id=category_id,
        type=type,
        description=description,
    )


@router.post("/transactions", response_model=TransactionResponse, status_code=201)
def create_transaction_api(data: TransactionCreate):
    return create_transaction(
        type=data.type,
        amount=data.amount,
        sent_date=data.date,
        category_id=data.category_id,
        description=data.description,
    )


@router.get("/transactions/{transaction_id}", response_model=TransactionResponse)
def get_transaction_api(transaction_id: int):
    return get_transaction(transaction_id)


@router.patch("/transactions/{transaction_id}", response_model=TransactionResponse)
def update_transaction_api(transaction_id: int, data: TransactionUpdate):
    return update_transaction(
        transaction_id,
        type=data.type,
        amount=data.amount,
        sent_date=data.date,
        category_id=data.category_id,
        description=data.description
    )


@router.delete("/transactions/{transaction_id}", status_code=204)
def delete_transaction_api(transaction_id: int):
    delete_transaction(transaction_id)
    return Response(status_code=204)
