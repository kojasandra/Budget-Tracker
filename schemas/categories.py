from typing import Annotated

from pydantic import BaseModel, ConfigDict, StringConstraints


CategoryName = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=30)]
CategoryColor = Annotated[str, StringConstraints(pattern=r"^#[0-9A-Fa-f]{6}$", min_length=7, max_length=7)]


class CategoryCreate(BaseModel):
    name: CategoryName
    color: CategoryColor


class CategoryUpdate(BaseModel):
    name: CategoryName | None = None
    color: CategoryColor | None = None


class CategoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    color: str
