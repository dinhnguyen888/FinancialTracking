import flet as ft
from apps.core.theme import AppColors, format_currency

class BalanceCard(ft.Container):
    def __init__(
        self,
        total_balance: float = 0.0,
        total_income: float = 0.0,
        total_expense: float = 0.0,
        on_add_click=None,
    ):
        self.total_balance = total_balance
        self.total_income = total_income
        self.total_expense = total_expense
        self.is_hidden = False
        self.on_add_click = on_add_click

        self.balance_text = ft.Text(
            value=format_currency(total_balance),
            size=30,
            weight=ft.FontWeight.BOLD,
            color=AppColors.TEXT_PRIMARY,
        )

        self.income_text = ft.Text(
            value=format_currency(total_income),
            size=14,
            weight=ft.FontWeight.W_600,
            color=AppColors.INCOME,
        )

        self.expense_text = ft.Text(
            value=format_currency(total_expense),
            size=14,
            weight=ft.FontWeight.W_600,
            color=AppColors.EXPENSE,
        )

        super().__init__(
            content=self._build_content(),
            bgcolor=AppColors.CARD_DARK,
            border_radius=24,
            padding=20,
            border=ft.Border.all(1, ft.Colors.with_opacity(0.12, AppColors.BORDER_DARK)),
            animate=ft.Animation(300, ft.AnimationCurve.EASE_OUT),
        )

    def _toggle_visibility(self, e):
        self.is_hidden = not self.is_hidden
        if self.is_hidden:
            self.balance_text.value = "•••••••• ₫"
            e.control.icon = ft.Icons.VISIBILITY_OFF
        else:
            self.balance_text.value = format_currency(self.total_balance)
            e.control.icon = ft.Icons.VISIBILITY
        if self.page:
            self.update()

    def update_values(self, balance: float, income: float, expense: float):
        self.total_balance = balance
        self.total_income = income
        self.total_expense = expense
        if not self.is_hidden:
            self.balance_text.value = format_currency(balance)
        self.income_text.value = format_currency(income)
        self.expense_text.value = format_currency(expense)
        if self.page:
            self.update()

    def _build_content(self) -> ft.Control:
        return ft.Column(
            spacing=16,
            controls=[
                # Top row: Label & Visibility Toggle
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Row(
                            spacing=6,
                            controls=[
                                ft.Container(
                                    content=ft.Icon(ft.Icons.ACCOUNT_BALANCE_WALLET_OUTLINED, color=AppColors.PRIMARY_LIGHT, size=16),
                                    bgcolor=ft.Colors.with_opacity(0.12, AppColors.PRIMARY),
                                    border_radius=6,
                                    padding=4,
                                ),
                                ft.Text(
                                    "Tổng số dư tháng này",
                                    size=12,
                                    weight=ft.FontWeight.W_500,
                                    color=AppColors.TEXT_MUTED,
                                ),
                            ]
                        ),
                        ft.IconButton(
                            icon=ft.Icons.VISIBILITY_OUTLINED,
                            icon_color=AppColors.TEXT_MUTED,
                            icon_size=18,
                            tooltip="Ẩn/Hiện số tiền",
                            on_click=self._toggle_visibility,
                        )
                    ]
                ),

                # Balance Amount
                ft.Container(
                    content=self.balance_text,
                    margin=ft.Margin.only(bottom=2),
                ),

                # Minimalist Sub-Cards: Income & Expense
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    spacing=12,
                    controls=[
                        # Income Container
                        ft.Container(
                            content=ft.Row(
                                spacing=8,
                                controls=[
                                    ft.Container(
                                        content=ft.Icon(ft.Icons.ARROW_DOWNWARD, color=AppColors.INCOME, size=14),
                                        bgcolor=ft.Colors.with_opacity(0.15, AppColors.INCOME),
                                        border_radius=14,
                                        padding=6,
                                    ),
                                    ft.Column(
                                        spacing=1,
                                        controls=[
                                            ft.Text("Thu nhập", size=11, color=AppColors.TEXT_MUTED),
                                            self.income_text,
                                        ]
                                    )
                                ]
                            ),
                            bgcolor=ft.Colors.with_opacity(0.04, ft.Colors.WHITE),
                            border_radius=14,
                            padding=ft.Padding.symmetric(horizontal=12, vertical=8),
                            expand=True,
                            border=ft.Border.all(1, ft.Colors.with_opacity(0.06, AppColors.BORDER_DARK)),
                        ),

                        # Expense Container
                        ft.Container(
                            content=ft.Row(
                                spacing=8,
                                controls=[
                                    ft.Container(
                                        content=ft.Icon(ft.Icons.ARROW_UPWARD, color=AppColors.EXPENSE, size=14),
                                        bgcolor=ft.Colors.with_opacity(0.15, AppColors.EXPENSE),
                                        border_radius=14,
                                        padding=6,
                                    ),
                                    ft.Column(
                                        spacing=1,
                                        controls=[
                                            ft.Text("Chi tiêu", size=11, color=AppColors.TEXT_MUTED),
                                            self.expense_text,
                                        ]
                                    )
                                ]
                            ),
                            bgcolor=ft.Colors.with_opacity(0.04, ft.Colors.WHITE),
                            border_radius=14,
                            padding=ft.Padding.symmetric(horizontal=12, vertical=8),
                            expand=True,
                            border=ft.Border.all(1, ft.Colors.with_opacity(0.06, AppColors.BORDER_DARK)),
                        ),
                    ]
                ),
            ]
        )
