from datetime import date

from fastapi import APIRouter, Response

from schemas.budgets import BudgetCreate, BudgetResponse, BudgetUpdate
from services.budgets import create_budget, delete_budget, get_budgets, update_budget


router = APIRouter(tags=["budgets"])


@router.get("/budgets", response_model=list[BudgetResponse])
def get_budgets_api(month: date):
    return get_budgets(month)


@router.post("/budgets", response_model=BudgetResponse, status_code=201)
def create_budget_api(data: BudgetCreate):
    return create_budget(sent_date=data.month, category_id=data.category_id, amount=data.amount)


@router.patch("/budgets/{budget_id}", response_model=BudgetResponse)
def update_budget_api(budget_id: int, data: BudgetUpdate):
    return update_budget(budget_id, amount=data.amount)


@router.delete("/budgets/{budget_id}", status_code=204)
def delete_budget_api(budget_id: int):
    delete_budget(budget_id)
    return Response(status_code=204)
