from enum import IntEnum
from dataclasses import dataclass
from typing import Optional

class CategoryType(IntEnum):
    INCOME = 0
    EXPENSE = 1

    @classmethod
    def from_str(cls, value: str) -> "CategoryType":
        if value.lower() in ("income", "thu nhập", "thu"):
            return cls.INCOME
        return cls.EXPENSE

@dataclass
class Category:
    id: Optional[int] = None
    name: str = ""
    description: str = ""
    type: CategoryType = CategoryType.EXPENSE
    is_active: bool = True
    icon: str = "category"
    color: str = "#6366F1"  # Default Indigo

    @property
    def is_income(self) -> bool:
        return self.type == CategoryType.INCOME

    @property
    def is_expense(self) -> bool:
        return self.type == CategoryType.EXPENSE
