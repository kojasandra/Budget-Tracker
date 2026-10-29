from fastapi import FastAPI
from routes.categories import router as categories_router
from routes.budgets import router as budgets_router
from routes.transactions import router as transactions_router
from routes.transaction_import import router as transaction_import_router
from routes.summary import router as summary_router


app = FastAPI()
app.include_router(categories_router)
app.include_router(budgets_router)
app.include_router(transaction_import_router)
app.include_router(transactions_router)
app.include_router(summary_router)


