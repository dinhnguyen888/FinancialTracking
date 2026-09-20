import flet as ft
from typing import Union, Callable, Optional
from apps.models.transaction import Income, Expense
from apps.core.theme import AppColors, format_currency

ICON_MAP = {
    "work": ft.Icons.WORK,
    "card_giftcard": ft.Icons.CARD_GIFTCARD,
    "trending_up": ft.Icons.TRENDING_UP,
    "laptop_chromebook": ft.Icons.LAPTOP_CHROMEBOOK,
    "account_balance_wallet": ft.Icons.ACCOUNT_BALANCE_WALLET,
    "restaurant": ft.Icons.RESTAURANT,
    "directions_car": ft.Icons.DIRECTIONS_CAR,
    "home": ft.Icons.HOME,
    "sports_esports": ft.Icons.SPORTS_ESPORTS,
    "favorite": ft.Icons.FAVORITE,
    "shopping_bag": ft.Icons.SHOPPING_BAG,
    "school": ft.Icons.SCHOOL,
    "receipt_long": ft.Icons.RECEIPT_LONG,
    "payments": ft.Icons.PAYMENTS,
    "category": ft.Icons.CATEGORY,
}

class TransactionCard(ft.Container):
    def __init__(
        self,
        tx: Union[Income, Expense],
        on_edit: Optional[Callable] = None,
        on_delete: Optional[Callable] = None,
    ):
        self.tx = tx
        self.on_edit = on_edit
        self.on_delete = on_delete

        is_income = isinstance(tx, Income)
        cat_color = tx.category.color if tx.category else (AppColors.INCOME if is_income else AppColors.EXPENSE)
        cat_icon_key = tx.category.icon if tx.category else "category"
        flet_icon = ICON_MAP.get(cat_icon_key, ft.Icons.CATEGORY)

        title = tx.description.strip() if tx.description.strip() else (tx.category.name if tx.category else "Giao dịch")
        cat_name = tx.category.name if tx.category else "Chưa phân loại"
        
        detail_tag = tx.source if is_income else tx.payment_method
        date_display = tx.date

        amount_str = format_currency(tx.amount, show_sign=True, is_income=is_income)
        amount_color = AppColors.INCOME if is_income else AppColors.EXPENSE

        badges = [
            ft.Container(
                content=ft.Text(cat_name, size=10, color=AppColors.TEXT_SECONDARY, weight=ft.FontWeight.W_500),
                bgcolor=ft.Colors.with_opacity(0.15, AppColors.BORDER_DARK),
                border_radius=6,
                padding=ft.Padding.symmetric(horizontal=6, vertical=2),
            ),
            ft.Container(
                content=ft.Text(detail_tag, size=10, color=AppColors.TEXT_MUTED),
                bgcolor=ft.Colors.with_opacity(0.1, AppColors.BORDER_DARK),
                border_radius=6,
                padding=ft.Padding.symmetric(horizontal=6, vertical=2),
            ),
        ]

        if not is_income and getattr(tx, "is_essential", False):
            badges.append(
                ft.Container(
                    content=ft.Text("Thiết yếu", size=10, color="#F59E0B", weight=ft.FontWeight.BOLD),
                    bgcolor=ft.Colors.with_opacity(0.15, "#F59E0B"),
                    border_radius=6,
                    padding=ft.Padding.symmetric(horizontal=6, vertical=2),
                )
            )

        super().__init__(
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    # Left: Icon & Info
                    ft.Row(
                        spacing=14,
                        expand=True,
                        controls=[
                            ft.Container(
                                content=ft.Icon(flet_icon, color=cat_color, size=22),
                                bgcolor=ft.Colors.with_opacity(0.15, cat_color),
                                border_radius=16,
                                width=46,
                                height=46,
                                alignment=ft.Alignment(0, 0),
                            ),
                            ft.Column(
                                spacing=4,
                                expand=True,
                                controls=[
                                    ft.Text(
                                        title,
                                        size=13,
                                        weight=ft.FontWeight.W_600,
                                        color=AppColors.TEXT_PRIMARY,
                                        max_lines=2,
                                        overflow=ft.TextOverflow.ELLIPSIS,
                                    ),
                                    ft.Row(
                                        spacing=6,
                                        wrap=True,
                                        controls=badges,
                                    ),
                                    ft.Text(date_display, size=11, color=AppColors.TEXT_MUTED),
                                ]
                            ),
                        ]
                    ),

                    # Right: Amount & Delete Action
                    ft.Column(
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.END,
                        spacing=4,
                        controls=[
                            ft.Text(
                                amount_str,
                                size=15,
                                weight=ft.FontWeight.BOLD,
                                color=amount_color,
                            ),
                            ft.IconButton(
                                icon=ft.Icons.DELETE_OUTLINE,
                                icon_size=18,
                                icon_color=ft.Colors.with_opacity(0.6, AppColors.EXPENSE),
                                tooltip="Xóa giao dịch",
                                on_click=lambda _: self.on_delete(self.tx) if self.on_delete else None,
                            ),
                        ]
                    ),
                ]
            ),
            bgcolor=AppColors.CARD_DARK,
            border_radius=16,
            padding=ft.Padding.symmetric(horizontal=14, vertical=12),
            border=ft.Border.all(1, ft.Colors.with_opacity(0.12, AppColors.BORDER_DARK)),
            ink=True,
            on_click=lambda _: self.on_edit(self.tx) if self.on_edit else None,
            animate=ft.Animation(200, ft.AnimationCurve.EASE_OUT),
        )
