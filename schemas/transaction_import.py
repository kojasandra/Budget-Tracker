from pydantic import BaseModel


class ImportRowError(BaseModel):
    row: int
    errors: list[str]


class TransactionImportResponse(BaseModel):
    imported: int
    failed: int
    errors: list[ImportRowError]
