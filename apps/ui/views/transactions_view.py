import flet as ft
from datetime import datetime
from apps.core.theme import AppColors, format_currency
from apps.core.events import EventBus, EVENT_TRANSACTION_UPDATED
from apps.database.repositories import IncomeRepository, ExpenseRepository, CategoryRepository
from apps.models.transaction import Income, Expense
from apps.ui.components.transaction_card import TransactionCard

class TransactionsView(ft.Container):
    def __init__(
        self,
        income_repo: IncomeRepository,
        expense_repo: ExpenseRepository,
        cat_repo: CategoryRepository,
        on_open_add=None,
        on_edit_tx=None,
    ):
        self.income_repo = income_repo
        self.expense_repo = expense_repo
        self.cat_repo = cat_repo
        self.on_open_add = on_open_add
        self.on_edit_tx = on_edit_tx

        self.current_filter_type = "ALL"  # "ALL", "EXPENSE", "INCOME"
        self.search_query = ""

        # Search field
        self.search_field = ft.TextField(
            hint_text="Tìm giao dịch, danh mục...",
            prefix_icon=ft.Icons.SEARCH,
            height=45,
            border_radius=12,
            border_color=ft.Colors.with_opacity(0.15, AppColors.BORDER_DARK),
            bgcolor=AppColors.CARD_DARK,
            content_padding=ft.Padding.only(left=10, right=10),
            on_change=self._on_search_change,
            expand=True,
        )

        # Summary total text for filtered view
        self.summary_text = ft.Text(
            value="",
            size=13,
            weight=ft.FontWeight.W_600,
            color=AppColors.TEXT_PRIMARY,
        )

        self.list_container = ft.Column(spacing=10)

        super().__init__(
            content=self._build_layout(),
            expand=True,
            padding=ft.Padding.only(left=16, right=16, top=28, bottom=0),
        )

        EventBus.subscribe(EVENT_TRANSACTION_UPDATED, self.refresh_data)
        self.refresh_data()

    def _build_layout(self) -> ft.Control:
        return ft.Column(
            spacing=14,
            expand=True,
            controls=[
                # Header & Filter Tabs
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Text("Lịch sử Giao dịch", size=20, weight=ft.FontWeight.BOLD, color=AppColors.TEXT_PRIMARY),
                        ft.IconButton(
                            icon=ft.Icons.ADD_CIRCLE,
                            icon_color=AppColors.PRIMARY,
                            icon_size=28,
                            tooltip="Thêm giao dịch",
                            on_click=lambda _: self.on_open_add() if self.on_open_add else None,
                        )
                    ]
                ),

                # Search bar
                ft.Row(controls=[self.search_field]),

                # Segmented Type Filter
                ft.Row(
                    spacing=8,
                    controls=[
                        self._filter_pill("Tất cả", "ALL"),
                        self._filter_pill("Chi tiêu", "EXPENSE"),
                        self._filter_pill("Thu nhập", "INCOME"),
                    ]
                ),

                # Summary Row
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Text("Danh sách", size=13, color=AppColors.TEXT_MUTED),
                        self.summary_text,
                    ]
                ),

                # Scrollable Transaction List
                ft.Container(
                    content=ft.ListView(
                        controls=[self.list_container],
                        expand=True,
                        spacing=10,
                    ),
                    expand=True,
                )
            ]
        )

    def _filter_pill(self, label: str, filter_val: str) -> ft.Control:
        is_selected = self.current_filter_type == filter_val
        return ft.Container(
            content=ft.Text(
                label,
                size=12,
                weight=ft.FontWeight.BOLD if is_selected else ft.FontWeight.NORMAL,
                color=ft.Colors.WHITE if is_selected else AppColors.TEXT_SECONDARY,
            ),
            bgcolor=AppColors.PRIMARY if is_selected else AppColors.CARD_DARK,
            border_radius=20,
            padding=ft.Padding.symmetric(horizontal=16, vertical=8),
            on_click=lambda _: self._set_filter(filter_val),
            ink=True,
            border=ft.Border.all(1, AppColors.PRIMARY if is_selected else ft.Colors.with_opacity(0.1, AppColors.BORDER_DARK)),
        )

    def _set_filter(self, filter_val: str):
        self.current_filter_type = filter_val
        # Re-render filter pills
        self.content.controls[2] = ft.Row(
            spacing=8,
            controls=[
                self._filter_pill("Tất cả", "ALL"),
                self._filter_pill("Chi tiêu", "EXPENSE"),
                self._filter_pill("Thu nhập", "INCOME"),
            ]
        )
        self.refresh_data()

    def _on_search_change(self, e):
        self.search_query = e.control.value.lower().strip()
        self.refresh_data()

    def refresh_data(self, *args, **kwargs):
        try:
            incomes = self.income_repo.get_all(limit=150) if self.current_filter_type in ("ALL", "INCOME") else []
            expenses = self.expense_repo.get_all(limit=150) if self.current_filter_type in ("ALL", "EXPENSE") else []

            all_tx = sorted(incomes + expenses, key=lambda x: (x.date, x.id or 0), reverse=True)

            # Apply search filter
            if self.search_query:
                filtered = []
                for t in all_tx:
                    desc_match = self.search_query in t.description.lower()
                    cat_match = t.category and (self.search_query in t.category.name.lower())
                    source_match = isinstance(t, Income) and (self.search_query in t.source.lower())
                    method_match = isinstance(t, Expense) and (self.search_query in t.payment_method.lower())
                    if desc_match or cat_match or source_match or method_match:
                        filtered.append(t)
                all_tx = filtered

            # Calculate summary
            total_inc = sum(t.amount for t in all_tx if isinstance(t, Income))
            total_exp = sum(t.amount for t in all_tx if isinstance(t, Expense))

            if self.current_filter_type == "ALL":
                self.summary_text.value = f"Thu: {format_currency(total_inc)} | Chi: {format_currency(total_exp)}"
            elif self.current_filter_type == "INCOME":
                self.summary_text.value = f"Tổng thu: {format_currency(total_inc)}"
            else:
                self.summary_text.value = f"Tổng chi: {format_currency(total_exp)}"

            self.list_container.controls.clear()
            if not all_tx:
                self.list_container.controls.append(
                    ft.Container(
                        content=ft.Column(
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=8,
                            controls=[
                                ft.Icon(ft.Icons.RECEIPT_LONG_OUTLINED, size=48, color=AppColors.TEXT_MUTED),
                                ft.Text("Không tìm thấy giao dịch nào", size=14, color=AppColors.TEXT_MUTED),
                            ]
                        ),
                        padding=40,
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
                    self.list_container.controls.append(card)

            # Bottom spacer to scroll above navigation bar
            self.list_container.controls.append(ft.Container(height=80))

            if self.page:
                self.update()
        except Exception:
            pass

    def _delete_tx(self, tx):
        if isinstance(tx, Income):
            self.income_repo.delete(tx.id)
        else:
            self.expense_repo.delete(tx.id)
        EventBus.publish(EVENT_TRANSACTION_UPDATED)
