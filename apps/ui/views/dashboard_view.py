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
        on_request_perm=None,
        is_perm_granted=True,
    ):
        self.income_repo = income_repo
        self.expense_repo = expense_repo
        self.notif_repo = notif_repo
        self.budget_repo = budget_repo
        self.on_navigate_tab = on_navigate_tab
        self.on_open_add = on_open_add
        self.on_edit_tx = on_edit_tx
        self.on_request_perm = on_request_perm
        self.is_perm_granted = is_perm_granted

        # 1. Minimalist Balance Card
        self.balance_card = BalanceCard(
            on_add_click=lambda: self.on_open_add("expense") if self.on_open_add else None,
        )

        # 2. Monthly Spending Budget Card
        self.budget_card = MonthlyBudgetCard(
            budget_repo=self.budget_repo,
            expense_repo=self.expense_repo,
        )

        # 3. Bank Notification Status Banner
        self.notification_banner = NotificationBanner(
            pending_count=0,
            permission_granted=self.is_perm_granted,
            on_review_click=lambda: self.on_navigate_tab(2) if self.on_navigate_tab else None,
            on_request_perm=self.on_request_perm,
        )

        # 4. Recent Transactions
        self.recent_list = ft.Column(spacing=10)

        super().__init__(
            content=self._build_layout(),
            expand=True,
            padding=ft.Padding.only(left=16, right=16, top=14, bottom=0),
        )

        EventBus.subscribe(EVENT_TRANSACTION_UPDATED, self.refresh_data)
        EventBus.subscribe(EVENT_NOTIFICATION_RECEIVED, self.refresh_notifications)
        self.refresh_data()

    def _build_layout(self) -> ft.Control:
        return ft.ListView(
            expand=True,
            spacing=16,
            controls=[
                # Minimalist Header: App Name & Date
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Column(
                            spacing=2,
                            controls=[
                                ft.Text(APP_NAME, size=22, weight=ft.FontWeight.BOLD, color=AppColors.TEXT_PRIMARY),
                                ft.Text(datetime.now().strftime("%d/%m/%Y"), size=12, color=AppColors.TEXT_MUTED),
                            ]
                        ),
                        ft.IconButton(
                            icon=ft.Icons.SECURITY_OUTLINED,
                            icon_color=AppColors.PRIMARY_LIGHT,
                            tooltip="Cài đặt quyền thông báo",
                            on_click=lambda _: self.on_request_perm() if self.on_request_perm else None,
                        )
                    ]
                ),

                # Balance Card
                self.balance_card,

                # Monthly Budget Progress Card (Định mức chi tiêu tháng)
                self.budget_card,

                # Notification Status
                self.notification_banner,

                # Minimalist Quick Actions (4 balanced buttons)
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    spacing=8,
                    controls=[
                        self._quick_btn(
                            ft.Icons.REMOVE,
                            "Chi tiêu",
                            AppColors.EXPENSE,
                            lambda: self.on_open_add("expense") if self.on_open_add else None
                        ),
                        self._quick_btn(
                            ft.Icons.ADD,
                            "Thu nhập",
                            AppColors.INCOME,
                            lambda: self.on_open_add("income") if self.on_open_add else None
                        ),
                        self._quick_btn(
                            ft.Icons.TRACK_CHANGES,
                            "Hạn mức",
                            AppColors.PRIMARY,
                            lambda: self.budget_card._open_edit_budget_dialog(None)
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

                # Bottom spacer so content clears the nav bar
                ft.Container(height=90),
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

    def refresh_notifications(self, is_perm_granted=None, *args, **kwargs):
        try:
            if is_perm_granted is not None:
                self.is_perm_granted = is_perm_granted
            pending = self.notif_repo.get_pending_count()
            self.notification_banner.set_state(pending, self.is_perm_granted)
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
