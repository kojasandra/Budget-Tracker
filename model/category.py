from sqlalchemy import CheckConstraint, String
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(
        String(30),
        CheckConstraint("char_length(name) BETWEEN 1 AND 30", name="ck_categories_name_length"),
        nullable=False,
        unique=True,
    )
    color: Mapped[str] = mapped_column(String(7), nullable=False)

