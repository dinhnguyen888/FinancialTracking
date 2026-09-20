import flet as ft
from datetime import datetime
from apps.core.theme import AppColors, format_currency
from apps.core.events import EventBus, EVENT_NOTIFICATION_RECEIVED, EVENT_TRANSACTION_UPDATED
from apps.database.repositories import BankNotificationRepository, CategoryRepository
from apps.services.notification_listener import NotificationService
from apps.models.notification import BankNotification
from apps.models.category import CategoryType

class PendingNotificationsView(ft.Container):
    def __init__(
        self,
        notif_service: NotificationService,
        notif_repo: BankNotificationRepository,
        cat_repo: CategoryRepository,
        on_navigate_dashboard=None,
    ):
        self.notif_service = notif_service
        self.notif_repo = notif_repo
        self.cat_repo = cat_repo
        self.on_navigate_dashboard = on_navigate_dashboard

        self.current_status_tab = "pending"  # "pending", "approved", "discarded"
        self.list_container = ft.Column(spacing=12)

        super().__init__(
            content=self._build_layout(),
            expand=True,
            padding=ft.Padding.only(left=16, right=16, top=10, bottom=0),
        )

        EventBus.subscribe(EVENT_NOTIFICATION_RECEIVED, self.refresh_data)
        EventBus.subscribe(EVENT_TRANSACTION_UPDATED, self.refresh_data)
        self.refresh_data()

    def _build_layout(self) -> ft.Control:
        return ft.Column(
            spacing=14,
            expand=True,
            controls=[
                # Minimalist Header
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Column(
                            spacing=2,
                            controls=[
                                ft.Text("Hộp thư Biến động số dư", size=20, weight=ft.FontWeight.BOLD, color=AppColors.TEXT_PRIMARY),
                                ft.Text("Tự động nhận diện từ Sacombank, Cake, MoMo...", size=12, color=AppColors.TEXT_MUTED),
                            ]
                        ),
                        ft.IconButton(
                            icon=ft.Icons.REFRESH,
                            icon_size=20,
                            icon_color=AppColors.PRIMARY_LIGHT,
                            bgcolor=AppColors.CARD_DARK,
                            tooltip="Làm mới",
                            on_click=lambda _: self.refresh_data(),
                        )

                    ]
                ),

                # Status Tabs
                ft.Row(
                    spacing=8,
                    controls=[
                        self._status_tab("Chờ duyệt", "pending"),
                        self._status_tab("Đã lưu", "approved"),
                        self._status_tab("Đã bỏ qua", "discarded"),
                    ]
                ),

                # List of Notifications
                ft.Container(
                    content=ft.ListView(
                        controls=[self.list_container],
                        expand=True,
                        spacing=12,
                        padding=ft.Padding.only(bottom=90),
                    ),
                    expand=True,
                )
            ]
        )

    def _status_tab(self, label: str, status_val: str) -> ft.Control:
        is_active = self.current_status_tab == status_val
        return ft.Container(
            content=ft.Text(
                label,
                size=12,
                weight=ft.FontWeight.BOLD if is_active else ft.FontWeight.NORMAL,
                color=ft.Colors.WHITE if is_active else AppColors.TEXT_SECONDARY,
            ),
            bgcolor=AppColors.PRIMARY if is_active else AppColors.CARD_DARK,
            border_radius=20,
            padding=ft.Padding.symmetric(horizontal=16, vertical=8),
            on_click=lambda _, val=status_val: self._set_tab(val),
            ink=True,
            border=ft.Border.all(1, AppColors.PRIMARY if is_active else ft.Colors.with_opacity(0.1, AppColors.BORDER_DARK)),
        )

    def _set_tab(self, val: str):
        self.current_status_tab = val
        self.content.controls[1] = ft.Row(
            spacing=8,
            controls=[
                self._status_tab("Chờ duyệt", "pending"),
                self._status_tab("Đã lưu", "approved"),
                self._status_tab("Đã bỏ qua", "discarded"),
            ]
        )
        self.refresh_data()

    def refresh_data(self, *args, **kwargs):
        try:
            notifs = self.notif_repo.get_all(status=self.current_status_tab)
            self.list_container.controls.clear()

            if not notifs:
                status_desc = {
                    "pending": "Không có thông báo nào đang chờ duyệt.",
                    "approved": "Chưa có thông báo nào đã duyệt.",
                    "discarded": "Không có thông báo nào bị bỏ qua."
                }.get(self.current_status_tab, "")

                self.list_container.controls.append(
                    ft.Container(
                        content=ft.Column(
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=10,
                            controls=[
                                ft.Icon(ft.Icons.MARK_EMAIL_READ_OUTLINED, size=48, color=AppColors.TEXT_MUTED),
                                ft.Text(status_desc, size=13, color=AppColors.TEXT_MUTED, text_align=ft.TextAlign.CENTER),
                                ft.Text(
                                    "Hệ thống sẽ tự động nhận diện thông báo từ Sacombank, Cake, MoMo khi phát sinh giao dịch.",
                                    size=11,
                                    color=AppColors.TEXT_MUTED,
                                    text_align=ft.TextAlign.CENTER
                                ) if self.current_status_tab == "pending" else ft.Container(),
                            ]
                        ),
                        padding=40,
                        alignment=ft.Alignment(0, 0),
                    )
                )
            else:
                for n in notifs:
                    card = self._build_notif_card(n)
                    self.list_container.controls.append(card)

            if self.page:
                self.update()
        except Exception:
            pass

    def _build_notif_card(self, n: BankNotification) -> ft.Control:
        is_income = n.transaction_type == "income"
        amount_color = AppColors.INCOME if is_income else AppColors.EXPENSE
        amount_str = format_currency(n.amount, show_sign=True, is_income=is_income)

        # Bank badge color
        bank_color = "#10B981" if "vcb" in n.bank_name.lower() or "vietcombank" in n.bank_name.lower() else (
            "#3B82F6" if "mb" in n.bank_name.lower() else (
                "#EC4899" if "momo" in n.bank_name.lower() else AppColors.PRIMARY
            )
        )

        # Category options
        target_type = CategoryType.INCOME if is_income else CategoryType.EXPENSE
        cats = self.cat_repo.get_by_type(target_type)
        cat_options = [ft.dropdown.Option(str(c.id), c.name) for c in cats]

        cat_dropdown = ft.Dropdown(
            value=str(n.suggested_category_id) if n.suggested_category_id else (str(cats[0].id) if cats else None),
            options=cat_options,
            height=40,
            border_radius=10,
            text_size=12,
            content_padding=ft.Padding.symmetric(horizontal=10, vertical=0),
            bgcolor=AppColors.BG_DARK,
            border_color=ft.Colors.with_opacity(0.15, AppColors.BORDER_DARK),
            expand=True,
        )

        actions = []
        if n.status == "pending":
            actions = [
                ft.OutlinedButton(
                    content=ft.Row(
                        spacing=4,
                        controls=[
                            ft.Icon(ft.Icons.CLOSE, size=14, color=AppColors.EXPENSE),
                            ft.Text("Bỏ qua", size=12, color=AppColors.EXPENSE),
                        ]
                    ),
                    style=ft.ButtonStyle(
                        side=ft.BorderSide(1, ft.Colors.with_opacity(0.3, AppColors.EXPENSE)),
                        shape=ft.RoundedRectangleBorder(radius=10),
                    ),
                    on_click=lambda _, nid=n.id: self._discard_notif(nid),
                ),
                ft.FilledButton(
                    content=ft.Row(
                        spacing=4,
                        controls=[
                            ft.Icon(ft.Icons.CHECK, size=16, color=ft.Colors.WHITE),
                            ft.Text("Lưu vào sổ", size=12, weight=ft.FontWeight.BOLD),
                        ]
                    ),
                    style=ft.ButtonStyle(
                        bgcolor=AppColors.PRIMARY,
                        shape=ft.RoundedRectangleBorder(radius=10),
                    ),
                    on_click=lambda _, nid=n.id, dd=cat_dropdown: self._approve_notif(nid, dd),
                )
            ]
        else:
            status_text = "Đã lưu vào thu/chi" if n.status == "approved" else "Đã bỏ qua"
            actions = [
                ft.Text(status_text, size=11, color=AppColors.INCOME if n.status == "approved" else AppColors.TEXT_MUTED)
            ]

        card_controls = [
            # Header: Bank + Time + Amount
            ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Row(
                        spacing=8,
                        controls=[
                            ft.Container(
                                content=ft.Text(n.bank_name, size=11, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                                bgcolor=bank_color,
                                border_radius=8,
                                padding=ft.Padding.symmetric(horizontal=8, vertical=3),
                            ),
                            ft.Text(n.received_at, size=11, color=AppColors.TEXT_MUTED),
                        ]
                    ),
                    ft.Text(amount_str, size=15, weight=ft.FontWeight.BOLD, color=amount_color),
                ]
            ),

            # Description
            ft.Text(
                n.detected_description or "Biến động số dư tài khoản",
                size=13,
                weight=ft.FontWeight.W_600,
                color=AppColors.TEXT_PRIMARY,
            ),

            # Raw snippet
            ft.Container(
                content=ft.Text(
                    n.raw_content,
                    size=10,
                    color=AppColors.TEXT_MUTED,
                    italic=True,
                    max_lines=2,
                    overflow=ft.TextOverflow.ELLIPSIS,
                ),
                bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.BLACK),
                border_radius=8,
                padding=8,
            ),
        ]

        if n.status == "pending":
            card_controls.extend([
                # Category selection on full width
                ft.Row(
                    spacing=8,
                    controls=[
                        ft.Icon(ft.Icons.CATEGORY_OUTLINED, size=16, color=AppColors.TEXT_MUTED),
                        ft.Text("Danh mục:", size=12, color=AppColors.TEXT_SECONDARY),
                        cat_dropdown,
                    ]
                ),
                # Action buttons row
                ft.Row(
                    alignment=ft.MainAxisAlignment.END,
                    spacing=8,
                    controls=actions,
                ),
            ])
        else:
            card_controls.append(
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Text(f"Danh mục: {n.suggested_category_name}", size=12, color=AppColors.TEXT_SECONDARY),
                        ft.Row(spacing=6, controls=actions),
                    ]
                )
            )

        return ft.Container(
            content=ft.Column(
                spacing=10,
                controls=card_controls,
            ),
            bgcolor=AppColors.CARD_DARK,
            border_radius=16,
            padding=14,
            border=ft.Border.all(1, ft.Colors.with_opacity(0.15, AppColors.BORDER_DARK)),
        )

    def _approve_notif(self, notif_id: int, dropdown: ft.Dropdown):
        cat_id = int(dropdown.value) if dropdown.value else None
        self.notif_service.approve_notification(notif_id, override_category_id=cat_id)
        if self.page:
            self.page.overlay.append(
                ft.SnackBar(content=ft.Text("Đã lưu giao dịch vào sổ thu/chi!"), bgcolor=AppColors.INCOME, open=True)
            )
            self.page.update()
        self.refresh_data()

    def _discard_notif(self, notif_id: int):
        self.notif_service.discard_notification(notif_id)
        self.refresh_data()
