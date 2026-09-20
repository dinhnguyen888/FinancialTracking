import flet as ft
from datetime import datetime
from typing import Optional, Union, Callable
from apps.core.theme import AppColors, format_currency
from apps.core.events import EventBus, EVENT_TRANSACTION_UPDATED
from apps.models.category import Category, CategoryType
from apps.models.transaction import Income, Expense
from apps.database.repositories import IncomeRepository, ExpenseRepository, CategoryRepository
from apps.ui.components.transaction_card import ICON_MAP

class AddTransactionBottomSheet(ft.BottomSheet):
    def __init__(
        self,
        income_repo: IncomeRepository,
        expense_repo: ExpenseRepository,
        cat_repo: CategoryRepository,
        existing_tx: Optional[Union[Income, Expense]] = None,
        on_saved: Optional[Callable] = None,
    ):
        self.income_repo = income_repo
        self.expense_repo = expense_repo
        self.cat_repo = cat_repo
        self.existing_tx = existing_tx
        self.on_saved = on_saved

        # Mode: "expense" or "income"
        if existing_tx:
            self.tx_type = "income" if isinstance(existing_tx, Income) else "expense"
            self.raw_amount_str = str(int(existing_tx.amount))
            self.selected_category_id = existing_tx.category_id
            self.current_date = existing_tx.date
            self.initial_desc = existing_tx.description
            self.is_essential = getattr(existing_tx, "is_essential", False)
            self.payment_method = getattr(existing_tx, "payment_method", "Chuyển khoản")
            self.source = getattr(existing_tx, "source", "Lương")
        else:
            self.tx_type = "expense"
            self.raw_amount_str = "0"
            self.selected_category_id = None
            self.current_date = datetime.now().strftime("%Y-%m-%d")
            self.initial_desc = ""
            self.is_essential = False
            self.payment_method = "Chuyển khoản"
            self.source = "Lương"

        # Amount Display
        self.amount_display = ft.Text(
            value=self._get_formatted_amount(),
            size=32,
            weight=ft.FontWeight.BOLD,
            color=AppColors.EXPENSE if self.tx_type == "expense" else AppColors.INCOME,
        )

        # Description input
        self.desc_input = ft.TextField(
            value=self.initial_desc,
            hint_text="Ghi chú (vd: Cơm trưa, Đổ xăng, Mua sắm...)",
            border_radius=12,
            bgcolor=AppColors.CARD_DARK,
            border_color=ft.Colors.with_opacity(0.15, AppColors.BORDER_DARK),
            content_padding=ft.Padding.all(12),
        )

        # Date input
        self.date_input = ft.TextField(
            value=self.current_date,
            hint_text="YYYY-MM-DD",
            prefix_icon=ft.Icons.CALENDAR_TODAY,
            border_radius=12,
            bgcolor=AppColors.CARD_DARK,
            border_color=ft.Colors.with_opacity(0.15, AppColors.BORDER_DARK),
            content_padding=ft.Padding.all(12),
            expand=True,
        )

        # Category Grid Container
        self.cat_grid = ft.Row(wrap=True, spacing=8)

        # Payment Method / Source dropdown
        self.method_dropdown = ft.Dropdown(
            value=self.payment_method if self.tx_type == "expense" else self.source,
            options=[
                ft.dropdown.Option("Chuyển khoản", "Chuyển khoản"),
                ft.dropdown.Option("Tiền mặt", "Tiền mặt"),
                ft.dropdown.Option("MoMo", "MoMo"),
                ft.dropdown.Option("Thẻ tín dụng", "Thẻ tín dụng"),
                ft.dropdown.Option("Lương", "Lương"),
                ft.dropdown.Option("Thưởng", "Thưởng"),
                ft.dropdown.Option("Đầu tư", "Đầu tư"),
                ft.dropdown.Option("Khác", "Khác"),
            ],
            border_radius=12,
            bgcolor=AppColors.CARD_DARK,
            border_color=ft.Colors.with_opacity(0.15, AppColors.BORDER_DARK),
            content_padding=ft.Padding.all(12),
            expand=True,
        )

        # Essential Switch (for Expense)
        self.essential_switch = ft.Switch(
            label="Khoản chi thiết yếu",
            value=self.is_essential,
            active_color=AppColors.PRIMARY,
        )

        super().__init__(
            content=self._build_content(),
            scrollable=True,
            bgcolor=AppColors.BG_DARK,
        )
        self._load_categories()

    def _get_formatted_amount(self) -> str:
        try:
            val = float(self.raw_amount_str) if self.raw_amount_str else 0.0
            return format_currency(val)
        except Exception:
            return "0 ₫"

    def _set_type(self, new_type: str):
        self.tx_type = new_type
        self.amount_display.color = AppColors.EXPENSE if new_type == "expense" else AppColors.INCOME
        self.selected_category_id = None
        self._load_categories()
        # Toggle type tabs visually
        self._update_type_tabs()
        self.update()

    def _update_type_tabs(self):
        is_exp = self.tx_type == "expense"
        self.type_tab_row.controls = [
            ft.Container(
                content=ft.Text("Chi tiêu (-)", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE if is_exp else AppColors.TEXT_SECONDARY),
                bgcolor=AppColors.EXPENSE if is_exp else AppColors.CARD_DARK,
                border_radius=12,
                padding=ft.Padding.symmetric(vertical=10),
                alignment=ft.Alignment(0, 0),
                expand=True,
                on_click=lambda _: self._set_type("expense"),
                ink=True,
            ),
            ft.Container(
                content=ft.Text("Thu nhập (+)", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE if not is_exp else AppColors.TEXT_SECONDARY),
                bgcolor=AppColors.INCOME if not is_exp else AppColors.CARD_DARK,
                border_radius=12,
                padding=ft.Padding.symmetric(vertical=10),
                alignment=ft.Alignment(0, 0),
                expand=True,
                on_click=lambda _: self._set_type("income"),
                ink=True,
            ),
        ]

    def _load_categories(self):
        cat_type = CategoryType.EXPENSE if self.tx_type == "expense" else CategoryType.INCOME
        categories = self.cat_repo.get_by_type(cat_type)

        if self.selected_category_id is None and categories:
            self.selected_category_id = categories[0].id

        self.cat_grid.controls.clear()
        for cat in categories:
            is_selected = cat.id == self.selected_category_id
            flet_icon = ICON_MAP.get(cat.icon, ft.Icons.CATEGORY)
            
            btn = ft.Container(
                content=ft.Row(
                    spacing=6,
                    controls=[
                        ft.Icon(flet_icon, size=16, color=cat.color if not is_selected else ft.Colors.WHITE),
                        ft.Text(cat.name, size=12, weight=ft.FontWeight.W_600 if is_selected else ft.FontWeight.NORMAL, color=ft.Colors.WHITE if is_selected else AppColors.TEXT_PRIMARY),
                    ]
                ),
                bgcolor=cat.color if is_selected else AppColors.CARD_DARK,
                border=ft.Border.all(1, cat.color if is_selected else ft.Colors.with_opacity(0.15, AppColors.BORDER_DARK)),
                border_radius=20,
                padding=ft.Padding.symmetric(horizontal=12, vertical=8),
                on_click=lambda _, c_id=cat.id: self._select_category(c_id),
                ink=True,
            )
            self.cat_grid.controls.append(btn)

    def _select_category(self, cat_id: int):
        self.selected_category_id = cat_id
        self._load_categories()
        self.update()

    def _on_numpad_key(self, key: str):
        if self.raw_amount_str == "0":
            if key != "000":
                self.raw_amount_str = key
        else:
            if len(self.raw_amount_str) < 12:  # Prevent integer overflow
                self.raw_amount_str += key
        self.amount_display.value = self._get_formatted_amount()
        self.update()

    def _on_numpad_backspace(self):
        if len(self.raw_amount_str) > 1:
            self.raw_amount_str = self.raw_amount_str[:-1]
        else:
            self.raw_amount_str = "0"
        self.amount_display.value = self._get_formatted_amount()
        self.update()

    def _on_numpad_clear(self):
        self.raw_amount_str = "0"
        self.amount_display.value = "0 ₫"
        self.update()

    def _save_transaction(self, e):
        amount = float(self.raw_amount_str) if self.raw_amount_str else 0.0
        if amount <= 0:
            if self.page:
                self.page.overlay.append(ft.SnackBar(content=ft.Text("Vui lòng nhập số tiền hợp lệ (> 0 ₫)"), open=True))
                self.page.update()
            return

        date_val = self.date_input.value.strip() or datetime.now().strftime("%Y-%m-%d")
        desc_val = self.desc_input.value.strip()

        if self.tx_type == "income":
            if self.existing_tx and isinstance(self.existing_tx, Income):
                self.existing_tx.amount = amount
                self.existing_tx.date = date_val
                self.existing_tx.description = desc_val
                self.existing_tx.category_id = self.selected_category_id
                self.existing_tx.source = self.method_dropdown.value or "Lương"
                self.income_repo.update(self.existing_tx)
            else:
                inc = Income(
                    amount=amount,
                    date=date_val,
                    description=desc_val,
                    category_id=self.selected_category_id,
                    source=self.method_dropdown.value or "Lương"
                )
                self.income_repo.add(inc)
        else:
            if self.existing_tx and isinstance(self.existing_tx, Expense):
                self.existing_tx.amount = amount
                self.existing_tx.date = date_val
                self.existing_tx.description = desc_val
                self.existing_tx.category_id = self.selected_category_id
                self.existing_tx.is_essential = self.essential_switch.value
                self.existing_tx.payment_method = self.method_dropdown.value or "Chuyển khoản"
                self.expense_repo.update(self.existing_tx)
            else:
                exp = Expense(
                    amount=amount,
                    date=date_val,
                    description=desc_val,
                    category_id=self.selected_category_id,
                    is_essential=self.essential_switch.value,
                    payment_method=self.method_dropdown.value or "Chuyển khoản"
                )
                self.expense_repo.add(exp)

        EventBus.publish(EVENT_TRANSACTION_UPDATED)
        self.open = False
        if self.page:
            self.page.update()
        if self.on_saved:
            self.on_saved()

    def _build_content(self) -> ft.Control:
        is_exp = self.tx_type == "expense"
        self.type_tab_row = ft.Row(
            spacing=10,
            controls=[
                ft.Container(
                    content=ft.Text("Chi tiêu (-)", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE if is_exp else AppColors.TEXT_SECONDARY),
                    bgcolor=AppColors.EXPENSE if is_exp else AppColors.CARD_DARK,
                    border_radius=12,
                    padding=ft.Padding.symmetric(vertical=10),
                    alignment=ft.Alignment(0, 0),
                    expand=True,
                    on_click=lambda _: self._set_type("expense"),
                    ink=True,
                ),
                ft.Container(
                    content=ft.Text("Thu nhập (+)", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE if not is_exp else AppColors.TEXT_SECONDARY),
                    bgcolor=AppColors.INCOME if not is_exp else AppColors.CARD_DARK,
                    border_radius=12,
                    padding=ft.Padding.symmetric(vertical=10),
                    alignment=ft.Alignment(0, 0),
                    expand=True,
                    on_click=lambda _: self._set_type("income"),
                    ink=True,
                ),
            ]
        )

        from apps.ui.components.numpad import MobileNumpad
        numpad = MobileNumpad(
            on_key=self._on_numpad_key,
            on_backspace=self._on_numpad_backspace,
            on_clear=self._on_numpad_clear
        )

        return ft.Container(
            content=ft.ListView(
                spacing=16,
                controls=[
                    # Handle bar
                    ft.Row(
                        alignment=ft.MainAxisAlignment.CENTER,
                        controls=[
                            ft.Container(
                                width=40,
                                height=4,
                                bgcolor=AppColors.TEXT_MUTED,
                                border_radius=2,
                            )
                        ]
                    ),

                    # Title & Close
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Text(
                                "Chỉnh sửa giao dịch" if self.existing_tx else "Thêm giao dịch mới",
                                size=18,
                                weight=ft.FontWeight.BOLD,
                                color=AppColors.TEXT_PRIMARY
                            ),
                            ft.IconButton(
                                icon=ft.Icons.CLOSE,
                                icon_size=20,
                                on_click=lambda _: self._close_sheet()
                            )
                        ]
                    ),

                    # Type Tabs
                    self.type_tab_row,

                    # Amount Display Container
                    ft.Container(
                        content=ft.Column(
                            alignment=ft.MainAxisAlignment.CENTER,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=4,
                            controls=[
                                ft.Text("Số tiền", size=12, color=AppColors.TEXT_MUTED),
                                self.amount_display,
                            ]
                        ),
                        bgcolor=AppColors.CARD_DARK,
                        border_radius=16,
                        padding=16,
                        border=ft.Border.all(1, ft.Colors.with_opacity(0.1, AppColors.BORDER_DARK)),
                    ),

                    # Quick Numpad
                    numpad,

                    # Category Section
                    ft.Column(
                        horizontal_alignment=ft.CrossAxisAlignment.START,
                        spacing=8,
                        controls=[
                            ft.Text("Chọn danh mục", size=13, weight=ft.FontWeight.BOLD, color=AppColors.TEXT_PRIMARY),
                            self.cat_grid,
                        ]
                    ),

                    # Note / Description
                    self.desc_input,

                    # Date & Method Row
                    ft.Row(
                        spacing=10,
                        controls=[self.date_input, self.method_dropdown]
                    ),

                    # Essential switch (Expense only)
                    self.essential_switch if self.tx_type == "expense" else ft.Container(),

                    # Save Button
                    ft.FilledButton(
                        content=ft.Row(
                            alignment=ft.MainAxisAlignment.CENTER,
                            spacing=8,
                            controls=[
                                ft.Icon(ft.Icons.CHECK, size=18, color=ft.Colors.WHITE),
                                ft.Text("Lưu giao dịch", size=15, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                            ]
                        ),
                        style=ft.ButtonStyle(
                            bgcolor=AppColors.PRIMARY,
                            shape=ft.RoundedRectangleBorder(radius=14),
                            padding=ft.Padding.symmetric(vertical=14),
                        ),
                        on_click=self._save_transaction,
                    ),
                    ft.Container(height=20)
                ]
            ),
            padding=ft.Padding.only(left=20, right=20, top=12, bottom=30),
            height=680,
            border_radius=ft.BorderRadius.vertical(top=24),
        )

    def _close_sheet(self):
        self.open = False
        if self.page:
            try:
                self.page.pop_dialog()
            except Exception:
                self.page.update()

