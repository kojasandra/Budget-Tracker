from fastapi import APIRouter, Query

from schemas.summary import CategorySummary, MonthlySummary
from services.summary import get_category_summary, get_monthly_summary


router = APIRouter(tags=["summary"])


@router.get("/summary", response_model=MonthlySummary)
def get_monthly_summary_api(
    year: int = Query(ge=1, le=9999),
    month: int = Query(ge=1, le=12),
):
    return get_monthly_summary(year, month)


@router.get("/summary/categories", response_model=list[CategorySummary])
def get_category_summary_api(
    year: int = Query(ge=1, le=9999),
    month: int = Query(ge=1, le=12),
):
    return get_category_summary(year, month)
