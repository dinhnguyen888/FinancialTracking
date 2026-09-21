import flet as ft
from datetime import datetime
from apps.core.theme import AppColors, format_currency
from apps.database.repositories import BudgetRepository, ExpenseRepository
from apps.core.events import EventBus, EVENT_TRANSACTION_UPDATED

class MonthlyBudgetCard(ft.Container):
    def __init__(
        self,
        budget_repo: BudgetRepository,
        expense_repo: ExpenseRepository,
        on_budget_changed=None,
    ):
        self.budget_repo = budget_repo
        self.expense_repo = expense_repo
        self.on_budget_changed = on_budget_changed

        now = datetime.now()
        self.current_year = now.year
        self.current_month = now.month

        # UI State Controls
        self.spent_text = ft.Text("0 ₫", size=20, weight=ft.FontWeight.BOLD, color=AppColors.TEXT_PRIMARY)
        self.limit_text = ft.Text("/ 10.000.000 ₫", size=13, color=AppColors.TEXT_MUTED)
        self.percent_badge = ft.Text("0%", size=11, weight=ft.FontWeight.BOLD, color=AppColors.PRIMARY_LIGHT)
        self.progress_bar = ft.ProgressBar(value=0.0, height=6, border_radius=3, color=AppColors.PRIMARY, bgcolor=AppColors.BORDER_DARK)
        self.status_text = ft.Text("Còn lại: 10.000.000 ₫", size=11, color=AppColors.TEXT_MUTED)

        super().__init__(
            content=self._build_content(),
            bgcolor=AppColors.CARD_DARK,
            border_radius=20,
            padding=16,
            border=ft.Border.all(1, ft.Colors.with_opacity(0.12, AppColors.BORDER_DARK)),
            ink=True,
            on_click=self._open_edit_budget_dialog,
        )

        self.refresh()

    def refresh(self):
        try:
            spent = self.expense_repo.get_total_for_month(self.current_year, self.current_month)
            limit = self.budget_repo.get_budget(self.current_year, self.current_month, default_limit=10000000.0)

            ratio = (spent / limit) if limit > 0 else 0.0
            percent = int(ratio * 100)

            self.spent_text.value = format_currency(spent)
            self.limit_text.value = f"/ {format_currency(limit)}"
            self.percent_badge.value = f"{percent}%"
            self.progress_bar.value = min(ratio, 1.0)

            if ratio > 1.0:
                over = spent - limit
                self.progress_bar.color = AppColors.EXPENSE
                self.percent_badge.color = AppColors.EXPENSE
                self.status_text.value = f"Vượt định mức: {format_currency(over)}"
                self.status_text.color = AppColors.EXPENSE
            elif ratio >= 0.8:
                rem = limit - spent
                self.progress_bar.color = AppColors.WARNING
                self.percent_badge.color = AppColors.WARNING
                self.status_text.value = f"Cảnh báo: Còn lại {format_currency(rem)}"
                self.status_text.color = AppColors.WARNING
            else:
                rem = limit - spent
                self.progress_bar.color = AppColors.INCOME
                self.percent_badge.color = AppColors.INCOME
                self.status_text.value = f"Còn lại: {format_currency(rem)} chi tiêu"
                self.status_text.color = AppColors.TEXT_MUTED

            if self.page:
                self.update()
        except Exception:
            pass

    def _build_content(self) -> ft.Control:
        return ft.Column(
            spacing=10,
            controls=[
                # Top header row
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Row(
                            spacing=8,
                            controls=[
                                ft.Container(
                                    content=ft.Icon(ft.Icons.TRACK_CHANGES, size=16, color=AppColors.PRIMARY_LIGHT),
                                    bgcolor=ft.Colors.with_opacity(0.12, AppColors.PRIMARY),
                                    border_radius=8,
                                    padding=6,
                                ),
                                ft.Column(
                                    spacing=1,
                                    controls=[
                                        ft.Text("Định mức chi tiêu tháng", size=13, weight=ft.FontWeight.W_600, color=AppColors.TEXT_PRIMARY),
                                        ft.Text(f"Tháng {self.current_month:02d}/{self.current_year}", size=11, color=AppColors.TEXT_MUTED),
                                    ]
                                )
                            ]
                        ),
                        ft.IconButton(
                            icon=ft.Icons.EDIT_OUTLINED,
                            icon_size=18,
                            icon_color=AppColors.TEXT_MUTED,
                            tooltip="Thay đổi định mức",
                            on_click=self._open_edit_budget_dialog,
                        )
                    ]
                ),

                # Numbers row (Spent vs Limit)
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.END,
                    controls=[
                        ft.Row(
                            spacing=4,
                            vertical_alignment=ft.CrossAxisAlignment.END,
                            controls=[
                                self.spent_text,
                                self.limit_text,
                            ]
                        ),
                        ft.Container(
                            content=self.percent_badge,
                            bgcolor=ft.Colors.with_opacity(0.1, AppColors.CARD_DARK_HOVER),
                            border_radius=6,
                            padding=ft.Padding.symmetric(horizontal=8, vertical=2),
                        )
                    ]
                ),

                # Progress bar
                self.progress_bar,

                # Bottom status text
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        self.status_text,
                        ft.Text("Chạm để điều chỉnh", size=10, color=AppColors.TEXT_MUTED),
                    ]
                )
            ]
        )

    def _open_edit_budget_dialog(self, e):
        if not self.page:
            return

        current_limit = self.budget_repo.get_budget(self.current_year, self.current_month, default_limit=10000000.0)
        input_limit = ft.TextField(
            value=f"{int(current_limit)}",
            label="Định mức chi tiêu tháng (VND)",
            keyboard_type=ft.KeyboardType.NUMBER,
            border_color=AppColors.PRIMARY,
            focused_border_color=AppColors.PRIMARY_LIGHT,
            color=AppColors.TEXT_PRIMARY,
            autofocus=True,
            suffix=ft.Text("₫", color=AppColors.TEXT_MUTED),
        )

        def set_preset(amount: float):
            input_limit.value = f"{int(amount)}"
            self.page.update()

        def save_budget(ev):
            try:
                val = float(input_limit.value.replace(".", "").replace(",", "").strip())
                if val > 0:
                    self.budget_repo.set_budget(self.current_year, self.current_month, val)
                    self.refresh()
                    if self.on_budget_changed:
                        self.on_budget_changed()
                    EventBus.publish(EVENT_TRANSACTION_UPDATED)
                    if hasattr(self.page, "pop_dialog"):
                        self.page.pop_dialog()
                    else:
                        dialog.open = False
                        self.page.update()
                    self.page.overlay.append(
                        ft.SnackBar(
                            content=ft.Text(f"Đã cập nhật định mức chi tiêu: {format_currency(val)}"),
                            bgcolor=AppColors.PRIMARY,
                            open=True,
                        )
                    )
                    self.page.update()
            except Exception as err:
                input_limit.error_text = "Vui lòng nhập số tiền hợp lệ"
                self.page.update()

        def close_dialog(ev):
            if hasattr(self.page, "pop_dialog"):
                self.page.pop_dialog()
            else:
                dialog.open = False
                self.page.update()

        dialog = ft.AlertDialog(
            title=ft.Row(
                spacing=8,
                controls=[
                    ft.Icon(ft.Icons.SAVINGS_OUTLINED, color=AppColors.PRIMARY_LIGHT, size=22),
                    ft.Text("Định mức chi tiêu tháng", size=16, weight=ft.FontWeight.BOLD),
                ]
            ),
            content=ft.Container(
                content=ft.Column(
                    tight=True,
                    spacing=14,
                    controls=[
                        ft.Text(
                            "Đặt hạn mức chi tối đa cho tháng này để theo dõi và kiểm soát tài chính.",
                            size=12,
                            color=AppColors.TEXT_MUTED,
                        ),
                        input_limit,
                        ft.Text("Gợi ý nhanh:", size=11, color=AppColors.TEXT_MUTED),
                        ft.Row(
                            spacing=6,
                            wrap=True,
                            controls=[
                                ft.Chip(label=ft.Text("5 triệu", size=11), on_click=lambda _: set_preset(5000000)),
                                ft.Chip(label=ft.Text("10 triệu", size=11), on_click=lambda _: set_preset(10000000)),
                                ft.Chip(label=ft.Text("15 triệu", size=11), on_click=lambda _: set_preset(15000000)),
                                ft.Chip(label=ft.Text("20 triệu", size=11), on_click=lambda _: set_preset(20000000)),
                            ]
                        )
                    ]
                ),
                width=320,
            ),
            actions=[
                ft.TextButton(content=ft.Text("Hủy", color=AppColors.TEXT_MUTED), on_click=close_dialog),
                ft.FilledButton(
                    content=ft.Text("Lưu định mức", weight=ft.FontWeight.BOLD),
                    style=ft.ButtonStyle(bgcolor=AppColors.PRIMARY),
                    on_click=save_budget,
                ),
            ],
            bgcolor=AppColors.BG_DARK,
        )

        if hasattr(self.page, "show_dialog"):
            self.page.show_dialog(dialog)
        else:
            self.page.overlay.append(dialog)
            dialog.open = True
            self.page.update()
