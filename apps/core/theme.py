import flet as ft

class AppColors:
    # Backgrounds & Surfaces
    BG_DARK = "#0B0F19"
    SURFACE_DARK = "#111827"
    CARD_DARK = "#1E293B"
    CARD_DARK_HOVER = "#273549"
    BORDER_DARK = "#334155"
    BORDER_LIGHT = "#E2E8F0"

    # Brand & Accents
    PRIMARY = "#6366F1"        # Indigo
    PRIMARY_LIGHT = "#818CF8"
    SECONDARY = "#8B5CF6"      # Violet
    ACCENT_CYAN = "#06B6D4"

    # Financial Status Colors
    INCOME = "#10B981"         # Emerald Green
    INCOME_BG = "#064E3B"
    EXPENSE = "#F43F5E"        # Rose / Coral
    EXPENSE_BG = "#4C0519"
    WARNING = "#F59E0B"        # Amber
    INFO = "#3B82F6"           # Sky Blue

    # Text
    TEXT_PRIMARY = "#F8FAFC"
    TEXT_SECONDARY = "#94A3B8"
    TEXT_MUTED = "#64748B"
    TEXT_WHITE = "#FFFFFF"

    # Gradients
    BALANCE_GRADIENT = [
        "#4F46E5",  # Deep Indigo
        "#7C3AED",  # Vibrant Violet
        "#9333EA",  # Purple
    ]

    INCOME_GRADIENT = ["#059669", "#10B981"]
    EXPENSE_GRADIENT = ["#E11D48", "#F43F5E"]


def format_currency(amount: float, show_sign: bool = False, is_income: bool = False) -> str:
    """Format float into Vietnamese currency string (e.g. +150.000 ₫)"""
    formatted = f"{abs(amount):,.0f}".replace(",", ".") + " ₫"
    if show_sign:
        sign = "+" if is_income else "-"
        return f"{sign}{formatted}"
    return formatted



def get_app_theme() -> ft.Theme:
    return ft.Theme(
        color_scheme_seed=AppColors.PRIMARY,
        font_family="sans-serif",
        use_material3=True,
    )
