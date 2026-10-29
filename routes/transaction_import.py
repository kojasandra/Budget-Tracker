from fastapi import APIRouter, File, UploadFile

from schemas.transaction_import import TransactionImportResponse
from services.transaction_import import import_transactions


router = APIRouter(tags=["transactions"])


@router.post("/transactions/import", response_model=TransactionImportResponse)
def import_transactions_api(file: UploadFile = File(...)):
    return import_transactions(file.file)
