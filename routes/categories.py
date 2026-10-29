from fastapi import APIRouter, Response

from schemas.categories import CategoryCreate, CategoryResponse, CategoryUpdate
from services.categories import (
    create_category,
    delete_category,
    get_categories,
    update_category,
)


router = APIRouter(tags=["categories"])


@router.get("/categories", response_model=list[CategoryResponse])
def get_all_categories_api():
    return get_categories()


@router.post("/categories", response_model=CategoryResponse, status_code=201)
def create_category_api(data: CategoryCreate):
    return create_category(name=data.name, color=data.color)


@router.patch("/categories/{category_id}", response_model=CategoryResponse)
def update_category_api(category_id: int, data: CategoryUpdate):
    return update_category(category_id, name=data.name, color=data.color)


@router.delete("/categories/{category_id}", status_code=204)
def delete_category_api(category_id: int):
    delete_category(category_id)
    return Response(status_code=204)
