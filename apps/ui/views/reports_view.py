import flet as ft
from datetime import datetime
from typing import Optional
from pathlib import Path
from apps.core.theme import AppColors, format_currency
from apps.core.events import EventBus, EVENT_TRANSACTION_UPDATED
from apps.database.repositories import IncomeRepository, ExpenseRepository, CategoryRepository
from apps.ui.components.transaction_card import ICON_MAP

class ReportsView(ft.Container):
    def __init__(
        self,
        income_repo: IncomeRepository,
        expense_repo: ExpenseRepository,
        cat_repo: CategoryRepository,
    ):
        self.income_repo = income_repo
        self.expense_repo = expense_repo
        self.cat_repo = cat_repo

        now = datetime.now()
        first_day = f"{now.year}-{now.month:02d}-01"
        import calendar
        last_day_num = calendar.monthrange(now.year, now.month)[1]
        last_day = f"{now.year}-{now.month:02d}-{last_day_num:02d}"

        self.start_date = first_day
        self.end_date = last_day

        # Summary text controls
        self.total_income_text = ft.Text("0 ₫", size=18, weight=ft.FontWeight.BOLD, color=AppColors.INCOME)
        self.total_expense_text = ft.Text("0 ₫", size=18, weight=ft.FontWeight.BOLD, color=AppColors.EXPENSE)
        self.balance_text = ft.Text("0 ₫", size=22, weight=ft.FontWeight.BOLD, color=AppColors.TEXT_WHITE)
        self.essential_text = ft.Text("0 ₫", size=13, weight=ft.FontWeight.BOLD, color=AppColors.WARNING)
        self.non_essential_text = ft.Text("0 ₫", size=13, weight=ft.FontWeight.BOLD, color=AppColors.TEXT_SECONDARY)

        self.essential_ratio_bar = ft.ProgressBar(value=0.5, color=AppColors.WARNING, bgcolor=AppColors.CARD_DARK, height=8, border_radius=4)

        # Dynamic containers for charts / category breakdown
        self.category_breakdown_list = ft.Column(spacing=10)
        self.monthly_comparison_list = ft.Column(spacing=10)

        super().__init__(
            content=self._build_layout(),
            expand=True,
            padding=ft.Padding.only(left=16, right=16, top=10, bottom=20),
        )

        EventBus.subscribe(EVENT_TRANSACTION_UPDATED, self.refresh_data)
        self.refresh_data()

    def _build_layout(self) -> ft.Control:
        return ft.ListView(
            expand=True,
            spacing=16,
            controls=[
                # Header
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Column(
                            spacing=2,
                            controls=[
                                ft.Text("Báo cáo & Phân tích", size=20, weight=ft.FontWeight.BOLD, color=AppColors.TEXT_PRIMARY),
                                ft.Text(f"Kỳ: {self.start_date} đến {self.end_date}", size=11, color=AppColors.TEXT_MUTED),
                            ]
                        ),
                        ft.Container(
                            content=ft.Icon(ft.Icons.ANALYTICS_OUTLINED, size=22, color=AppColors.PRIMARY_LIGHT),
                            bgcolor=AppColors.CARD_DARK,
                            border_radius=12,
                            padding=8,
                        )
                    ]
                ),

                # Net Balance Card
                ft.Container(
                    content=ft.Column(
                        spacing=12,
                        controls=[
                            ft.Row(
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                controls=[
                                    ft.Text("Số dư ròng kỳ này", size=13, color=AppColors.TEXT_SECONDARY),
                                    ft.Icon(ft.Icons.TRENDING_UP, color=AppColors.PRIMARY_LIGHT, size=18),
                                ]
                            ),
                            self.balance_text,
                            ft.Divider(height=1, color=ft.Colors.with_opacity(0.1, AppColors.BORDER_DARK)),
                            ft.Row(
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                controls=[
                                    ft.Column(
                                        spacing=2,
                                        controls=[
                                            ft.Text("Tổng thu nhập", size=11, color=AppColors.TEXT_MUTED),
                                            self.total_income_text,
                                        ]
                                    ),
                                    ft.Column(
                                        horizontal_alignment=ft.CrossAxisAlignment.END,
                                        spacing=2,
                                        controls=[
                                            ft.Text("Tổng chi tiêu", size=11, color=AppColors.TEXT_MUTED),
                                            self.total_expense_text,
                                        ]
                                    ),
                                ]
                            )
                        ]
                    ),
                    bgcolor=AppColors.CARD_DARK,
                    border_radius=20,
                    padding=18,
                    border=ft.Border.all(1, ft.Colors.with_opacity(0.12, AppColors.BORDER_DARK)),
                ),

                # Essential vs Non-essential Analysis Card
                ft.Container(
                    content=ft.Column(
                        spacing=10,
                        controls=[
                            ft.Row(
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                controls=[
                                    ft.Text("Chi tiêu Thiết yếu vs Tùy ý", size=14, weight=ft.FontWeight.BOLD, color=AppColors.TEXT_PRIMARY),
                                    ft.Icon(ft.Icons.PIE_CHART_OUTLINE, color=AppColors.WARNING, size=18),
                                ]
                            ),
                            self.essential_ratio_bar,
                            ft.Row(
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                controls=[
                                    ft.Row(
                                        spacing=6,
                                        controls=[
                                            ft.Container(width=10, height=10, bgcolor=AppColors.WARNING, border_radius=5),
                                            ft.Text("Thiết yếu: ", size=11, color=AppColors.TEXT_MUTED),
                                            self.essential_text,
                                        ]
                                    ),
                                    ft.Row(
                                        spacing=6,
                                        controls=[
                                            ft.Container(width=10, height=10, bgcolor=AppColors.TEXT_MUTED, border_radius=5),
                                            ft.Text("Tùy ý: ", size=11, color=AppColors.TEXT_MUTED),
                                            self.non_essential_text,
                                        ]
                                    ),
                                ]
                            )
                        ]
                    ),
                    bgcolor=AppColors.CARD_DARK,
                    border_radius=18,
                    padding=16,
                    border=ft.Border.all(1, ft.Colors.with_opacity(0.1, AppColors.BORDER_DARK)),
                ),

                # Category Breakdown Section
                ft.Text("Cơ cấu Chi tiêu theo Danh mục", size=16, weight=ft.FontWeight.BOLD, color=AppColors.TEXT_PRIMARY),
                self.category_breakdown_list,

                # Monthly Trend Section
                ft.Text("Xu hướng Thu / Chi gần đây", size=16, weight=ft.FontWeight.BOLD, color=AppColors.TEXT_PRIMARY),
                self.monthly_comparison_list,
            ]
        )

    def refresh_data(self, *args, **kwargs):
        try:
            incomes = self.income_repo.get_by_date_range(self.start_date, self.end_date)
            expenses = self.expense_repo.get_by_date_range(self.start_date, self.end_date)

            total_inc = sum(i.amount for i in incomes)
            total_exp = sum(e.amount for e in expenses)
            net_balance = total_inc - total_exp

            essential_sum = sum(e.amount for e in expenses if e.is_essential)
            non_essential_sum = total_exp - essential_sum

            self.total_income_text.value = format_currency(total_inc)
            self.total_expense_text.value = format_currency(total_exp)
            self.balance_text.value = format_currency(net_balance, show_sign=True, is_income=net_balance >= 0)
            self.essential_text.value = format_currency(essential_sum)
            self.non_essential_text.value = format_currency(non_essential_sum)

            if total_exp > 0:
                self.essential_ratio_bar.value = min(1.0, essential_sum / total_exp)
            else:
                self.essential_ratio_bar.value = 0.0

            # 1. Category Breakdown
            grouped_cats = self.expense_repo.get_totals_grouped_by_category(self.start_date, self.end_date)
            self.category_breakdown_list.controls.clear()

            if not grouped_cats:
                self.category_breakdown_list.controls.append(
                    ft.Text("Chưa có dữ liệu chi tiêu trong kỳ này.", size=13, color=AppColors.TEXT_MUTED)
                )
            else:
                for item in grouped_cats:
                    pct = (item["total"] / total_exp) * 100 if total_exp > 0 else 0
                    flet_icon = ICON_MAP.get(item["icon"], ft.Icons.CATEGORY)
                    cat_color = item["color"] or AppColors.PRIMARY

                    row_card = ft.Container(
                        content=ft.Column(
                            spacing=6,
                            controls=[
                                ft.Row(
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                    controls=[
                                        ft.Row(
                                            spacing=10,
                                            controls=[
                                                ft.Icon(flet_icon, color=cat_color, size=18),
                                                ft.Text(item["name"], size=13, weight=ft.FontWeight.W_600, color=AppColors.TEXT_PRIMARY),
                                            ]
                                        ),
                                        ft.Row(
                                            spacing=8,
                                            controls=[
                                                ft.Text(format_currency(item["total"]), size=13, weight=ft.FontWeight.BOLD, color=AppColors.TEXT_PRIMARY),
                                                ft.Text(f"({pct:.1f}%)", size=11, color=AppColors.TEXT_MUTED),
                                            ]
                                        )
                                    ]
                                ),
                                ft.ProgressBar(
                                    value=pct / 100.0,
                                    color=cat_color,
                                    bgcolor=ft.Colors.with_opacity(0.15, AppColors.BORDER_DARK),
                                    height=6,
                                    border_radius=3,
                                )
                            ]
                        ),
                        bgcolor=AppColors.CARD_DARK,
                        border_radius=14,
                        padding=12,
                    )
                    self.category_breakdown_list.controls.append(row_card)

            # 2. Monthly Trend (last 3 months)
            now = datetime.now()
            self.monthly_comparison_list.controls.clear()
            for offset in range(2, -1, -1):
                m = now.month - offset
                y = now.year
                if m <= 0:
                    m += 12
                    y -= 1
                m_inc = self.income_repo.get_total_for_month(y, m)
                m_exp = self.expense_repo.get_total_for_month(y, m)

                month_card = ft.Container(
                    content=ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Text(f"Tháng {m:02d}/{y}", size=13, weight=ft.FontWeight.W_600, color=AppColors.TEXT_PRIMARY),
                            ft.Row(
                                spacing=16,
                                controls=[
                                    ft.Row(
                                        spacing=4,
                                        controls=[
                                            ft.Icon(ft.Icons.TRENDING_UP, size=14, color=AppColors.INCOME),
                                            ft.Text(f"+{format_currency(m_inc)}", size=12, color=AppColors.INCOME, weight=ft.FontWeight.W_500),
                                        ]
                                    ),
                                    ft.Row(
                                        spacing=4,
                                        controls=[
                                            ft.Icon(ft.Icons.TRENDING_DOWN, size=14, color=AppColors.EXPENSE),
                                            ft.Text(f"-{format_currency(m_exp)}", size=12, color=AppColors.EXPENSE, weight=ft.FontWeight.W_500),
                                        ]
                                    ),
                                ]
                            )
                        ]
                    ),
                    bgcolor=AppColors.CARD_DARK,
                    border_radius=12,
                    padding=12,
                )
                self.monthly_comparison_list.controls.append(month_card)

            if self.page:
                self.update()
        except Exception:
            pass
