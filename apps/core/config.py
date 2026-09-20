import os
from pathlib import Path

# Detect Android mobile sandbox for writable storage directory
if "ANDROID_DATA" in os.environ or "FLET_APP_STORAGE_DATA" in os.environ:
    app_storage = os.environ.get("FLET_APP_STORAGE_DATA") or str(Path.home())
    DATA_DIR = Path(app_storage)
else:
    BASE_DIR = Path(__file__).resolve().parent.parent
    DATA_DIR = BASE_DIR / "data"

try:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
except Exception:
    import tempfile
    DATA_DIR = Path(tempfile.gettempdir())

DB_PATH = DATA_DIR / "finance.db"

APP_NAME = "CashflowTracking"
APP_SUBTITLE = "Quản lý Tài chính Cá nhân & Bắt biến động số dư"

# Default seed categories with icons & modern theme colors
DEFAULT_INCOME_CATEGORIES = [
    {"name": "Lương", "description": "Thu nhập tiền lương cố định hàng tháng", "icon": "work", "color": "#10B981"},
    {"name": "Thưởng", "description": "Thưởng doanh số, thưởng lễ Tết", "icon": "card_giftcard", "color": "#06B6D4"},
    {"name": "Đầu tư", "description": "Lãi cổ phiếu, trái phiếu, tiết kiệm", "icon": "trending_up", "color": "#3B82F6"},
    {"name": "Freelance", "description": "Làm thêm ngoài giờ, dự án tự do", "icon": "laptop_chromebook", "color": "#8B5CF6"},
    {"name": "Thu nhập khác", "description": "Các khoản thu khác không phân loại", "icon": "account_balance_wallet", "color": "#6B7280"},
]

DEFAULT_EXPENSE_CATEGORIES = [
    {"name": "Ăn uống", "description": "Cơm trưa, cà phê, đi chợ, siêu thị", "icon": "restaurant", "color": "#EF4444"},
    {"name": "Đi lại", "description": "Xăng xe, gửi xe, Grab, taxi", "icon": "directions_car", "color": "#F97316"},
    {"name": "Nhà cửa", "description": "Tiền thuê nhà, bảo trì, đồ gia dụng", "icon": "home", "color": "#F59E0B"},
    {"name": "Giải trí", "description": "Xem phim, game, du lịch, giao lưu", "icon": "sports_esports", "color": "#EC4899"},
    {"name": "Sức khỏe", "description": "Thuốc men, khám bệnh, thể thao, gym", "icon": "favorite", "color": "#14B8A6"},
    {"name": "Mua sắm", "description": "Quần áo, mỹ phẩm, đồ công nghệ", "icon": "shopping_bag", "color": "#8B5CF6"},
    {"name": "Giáo dục", "description": "Sách báo, khóa học, học phí", "icon": "school", "color": "#6366F1"},
    {"name": "Hóa đơn & Tiện ích", "description": "Điện, nước, internet, điện thoại", "icon": "receipt_long", "color": "#64748B"},
    {"name": "Chi tiêu khác", "description": "Các khoản chi phát sinh khác", "icon": "payments", "color": "#94A3B8"},
]
