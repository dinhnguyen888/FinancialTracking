from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime

@dataclass
class BankNotification:
    id: Optional[int] = None
    bank_name: str = "Ngân hàng"
    raw_content: str = ""
    received_at: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    amount: float = 0.0
    transaction_type: str = "expense"  # "income" or "expense"
    detected_description: str = ""
    suggested_category_id: Optional[int] = None
    suggested_category_name: str = "Chưa phân loại"
    status: str = "pending"  # "pending", "approved", "discarded"
    created_transaction_id: Optional[int] = None

@dataclass
class ParseResult:
    is_valid: bool = False
    bank_name: str = ""
    amount: float = 0.0
    transaction_type: str = "expense"  # "income" or "expense"
    description: str = ""
    suggested_category: str = "Chi tiêu khác"
    balance: Optional[float] = None
    transaction_time: Optional[str] = None
    raw_message: str = ""
