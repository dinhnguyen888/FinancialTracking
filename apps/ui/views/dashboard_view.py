import flet as ft
from datetime import datetime
from apps.core.theme import AppColors
from apps.core.config import APP_NAME
from apps.core.events import EventBus, EVENT_TRANSACTION_UPDATED, EVENT_NOTIFICATION_RECEIVED
from apps.database.repositories import IncomeRepository, ExpenseRepository, BankNotificationRepository, BudgetRepository
from apps.ui.components.balance_card import BalanceCard
from apps.ui.components.monthly_budget_card import MonthlyBudgetCard
from apps.ui.components.notification_banner import NotificationBanner
from apps.ui.components.transaction_card import TransactionCard

class DashboardView(ft.Container):
    def __init__(
        self,
        income_repo: IncomeRepository,
        expense_repo: ExpenseRepository,
        notif_repo: BankNotificationRepository,
        budget_repo: BudgetRepository,
        on_navigate_tab=None,
        on_open_add=None,
        on_edit_tx=None,
        get_permission_status=None,
        on_request_permission=None,
    ):
        self.income_repo = income_repo
        self.expense_repo = expense_repo
        self.notif_repo = notif_repo
        self.budget_repo = budget_repo
        self.on_navigate_tab = on_navigate_tab
        self.on_open_add = on_open_add
        self.on_edit_tx = on_edit_tx
        self.get_permission_status = get_permission_status
        self.on_request_permission = on_request_permission

        # 1. Minimalist Balance Card
        self.balance_card = BalanceCard(
            on_add_click=self.on_open_add,
        )

        # 2. Monthly Spending Budget Card
        self.budget_card = MonthlyBudgetCard(
            budget_repo=self.budget_repo,
            expense_repo=self.expense_repo,
        )

        # 3. Bank Notification Status Banner
        self.notification_banner = NotificationBanner(
            pending_count=0,
            permission_granted=True,
            on_review_click=lambda: self.on_navigate_tab(2) if self.on_navigate_tab else None,
            on_request_permission=self.on_request_permission,
        )

        # 4. Recent Transactions
        self.recent_list = ft.Column(spacing=10)

        super().__init__(
            content=self._build_layout(),
            expand=True,
            padding=ft.Padding.only(left=16, right=16, top=28, bottom=0),
        )

        EventBus.subscribe(EVENT_TRANSACTION_UPDATED, self.refresh_data)
        EventBus.subscribe(EVENT_NOTIFICATION_RECEIVED, self.refresh_notifications)
        self.refresh_data()

    def _build_layout(self) -> ft.Control:
        return ft.ListView(
            expand=True,
            spacing=16,
            controls=[
                # Minimalist Header: App Name & Date (NO top bell icon as requested)
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Column(
                            spacing=2,
                            controls=[
                                ft.Text(APP_NAME, size=22, weight=ft.FontWeight.BOLD, color=AppColors.TEXT_PRIMARY),
                                ft.Text(datetime.now().strftime("%A, %d/%m/%Y"), size=12, color=AppColors.TEXT_MUTED),
                            ]
                        ),
                        ft.Container(
                            content=ft.Row(
                                spacing=6,
                                controls=[
                                    ft.Container(width=6, height=6, border_radius=3, bgcolor=AppColors.INCOME),
                                    ft.Text("Online", size=11, weight=ft.FontWeight.W_500, color=AppColors.TEXT_MUTED),
                                ]
                            ),
                            bgcolor=ft.Colors.with_opacity(0.06, ft.Colors.WHITE),
                            border_radius=12,
                            padding=ft.Padding.symmetric(horizontal=10, vertical=6),
                            border=ft.Border.all(1, ft.Colors.with_opacity(0.08, AppColors.BORDER_DARK)),
                        )
                    ]
                ),

                # Balance Card
                self.balance_card,

                # Monthly Budget Progress Card (Định mức chi tiêu tháng)
                self.budget_card,

                # Notification Status
                self.notification_banner,

                # Minimalist Quick Actions (No test simulate buttons)
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    spacing=12,
                    controls=[
                        self._quick_btn(
                            ft.Icons.ADD,
                            "Thêm thu chi",
                            AppColors.PRIMARY,
                            self.on_open_add
                        ),
                        self._quick_btn(
                            ft.Icons.PIE_CHART_OUTLINE,
                            "Báo cáo",
                            AppColors.SECONDARY,
                            lambda: self.on_navigate_tab(3) if self.on_navigate_tab else None
                        ),
                        self._quick_btn(
                            ft.Icons.INBOX_OUTLINED,
                            "Hộp thư",
                            AppColors.ACCENT_CYAN,
                            lambda: self.on_navigate_tab(2) if self.on_navigate_tab else None
                        ),
                    ]
                ),

                # Recent Transactions Header
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Text("Giao dịch gần đây", size=15, weight=ft.FontWeight.BOLD, color=AppColors.TEXT_PRIMARY),
                        ft.TextButton(
                            content=ft.Text("Xem tất cả", size=12, color=AppColors.PRIMARY_LIGHT),
                            on_click=lambda _: self.on_navigate_tab(1) if self.on_navigate_tab else None,
                        )
                    ]
                ),

                # List of Recent Transactions
                self.recent_list,

                # Bottom spacer to scroll above navigation bar
                ft.Container(height=80),
            ]
        )

    def _quick_btn(self, icon, label, color, on_click):
        return ft.Container(
            content=ft.Column(
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=6,
                controls=[
                    ft.Container(
                        content=ft.Icon(icon, color=color, size=20),
                        bgcolor=ft.Colors.with_opacity(0.12, color),
                        border_radius=12,
                        padding=8,
                    ),
                    ft.Text(label, size=11, weight=ft.FontWeight.W_500, color=AppColors.TEXT_PRIMARY, text_align=ft.TextAlign.CENTER),
                ]
            ),
            bgcolor=AppColors.CARD_DARK,
            border_radius=16,
            padding=ft.Padding.symmetric(vertical=10, horizontal=8),
            expand=True,
            on_click=lambda _: on_click() if on_click else None,
            ink=True,
            border=ft.Border.all(1, ft.Colors.with_opacity(0.1, AppColors.BORDER_DARK)),
        )

    def refresh_notifications(self, *args, **kwargs):
        try:
            pending = self.notif_repo.get_pending_count()
            is_granted = self.get_permission_status() if self.get_permission_status else True
            self.notification_banner.update_state(pending, is_granted)
        except Exception:
            pass

    def refresh_data(self, *args, **kwargs):
        try:
            now = datetime.now()
            income = self.income_repo.get_total_for_month(now.year, now.month)
            expense = self.expense_repo.get_total_for_month(now.year, now.month)
            balance = income - expense

            self.balance_card.update_values(balance, income, expense)
            self.budget_card.refresh()
            self.refresh_notifications()

            # Load recent transactions
            incomes = self.income_repo.get_all(limit=8)
            expenses = self.expense_repo.get_all(limit=8)
            all_tx = sorted(incomes + expenses, key=lambda x: (x.date, x.id or 0), reverse=True)[:5]

            self.recent_list.controls.clear()
            if not all_tx:
                self.recent_list.controls.append(
                    ft.Container(
                        content=ft.Column(
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=6,
                            controls=[
                                ft.Icon(ft.Icons.RECEIPT_LONG_OUTLINED, size=36, color=AppColors.TEXT_MUTED),
                                ft.Text("Chưa có giao dịch nào", size=12, color=AppColors.TEXT_MUTED),
                            ]
                        ),
                        padding=24,
                        alignment=ft.Alignment(0, 0),
                    )
                )
            else:
                for tx in all_tx:
                    card = TransactionCard(
                        tx=tx,
                        on_edit=self.on_edit_tx,
                        on_delete=self._delete_tx,
                    )
                    self.recent_list.controls.append(card)

            if self.page:
                self.update()
        except Exception:
            pass

    def _delete_tx(self, tx):
        from apps.models.transaction import Income
        if isinstance(tx, Income):
            self.income_repo.delete(tx.id)
        else:
            self.expense_repo.delete(tx.id)
        EventBus.publish(EVENT_TRANSACTION_UPDATED)
