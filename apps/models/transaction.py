from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime
from apps.models.category import Category

@dataclass
class Transaction:
    id: Optional[int] = None
    amount: float = 0.0
    date: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d"))
    description: str = ""
    category_id: Optional[int] = None
    category: Optional[Category] = None

@dataclass
class Income(Transaction):
    source: str = "Khác"

    @property
    def transaction_type_name(self) -> str:
        return "Thu nhập"

@dataclass
class Expense(Transaction):
    is_essential: bool = False
    payment_method: str = "Chuyển khoản"

    @property
    def transaction_type_name(self) -> str:
        return "Chi tiêu"
