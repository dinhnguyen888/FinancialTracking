import flet as ft
from apps.core.theme import AppColors

class NotificationBanner(ft.Container):
    def __init__(
        self,
        pending_count: int = 0,
        permission_granted: bool = True,
        on_review_click=None,
        on_request_permission=None,
    ):
        self.pending_count = pending_count
        self.permission_granted = permission_granted
        self.on_review_click = on_review_click
        self.on_request_permission = on_request_permission

        super().__init__(
            content=self._build_content(),
            bgcolor=self._get_bg_color(),
            border=self._get_border(),
            border_radius=16,
            padding=ft.Padding.symmetric(horizontal=14, vertical=10),
            animate=ft.Animation(300, ft.AnimationCurve.EASE_OUT),
        )

    def _get_bg_color(self):
        if not self.permission_granted:
            return ft.Colors.with_opacity(0.08, AppColors.EXPENSE)
        if self.pending_count > 0:
            return ft.Colors.with_opacity(0.08, AppColors.PRIMARY)
        return AppColors.CARD_DARK

    def _get_border(self):
        if not self.permission_granted:
            return ft.Border.all(1, ft.Colors.with_opacity(0.3, AppColors.EXPENSE))
        if self.pending_count > 0:
            return ft.Border.all(1, AppColors.PRIMARY)
        return ft.Border.all(1, ft.Colors.with_opacity(0.12, AppColors.BORDER_DARK))

    def update_state(self, pending_count: int, permission_granted: bool):
        self.pending_count = pending_count
        self.permission_granted = permission_granted
        self.content = self._build_content()
        self.bgcolor = self._get_bg_color()
        self.border = self._get_border()
        if self.page:
            self.update()

    def set_count(self, count: int):
        self.update_state(count, self.permission_granted)

    def _build_content(self) -> ft.Control:
        if not self.permission_granted:
            return ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Row(
                        expand=True,
                        spacing=8,
                        controls=[
                            ft.Container(
                                width=8,
                                height=8,
                                border_radius=4,
                                bgcolor=AppColors.EXPENSE,
                            ),
                            ft.Column(
                                spacing=1,
                                expand=True,
                                controls=[
                                    ft.Text("Chưa cấp quyền nhận thông báo", size=11, weight=ft.FontWeight.BOLD, color=AppColors.TEXT_PRIMARY),
                                    ft.Text("Bấm để tự động bắt tiền Sacombank, MoMo, Cake", size=10, color=AppColors.TEXT_MUTED, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                                ]
                            )
                        ]
                    ),
                    ft.FilledButton(
                        content=ft.Text("Bật ngay", size=11, weight=ft.FontWeight.BOLD),
                        style=ft.ButtonStyle(bgcolor=AppColors.PRIMARY),
                        on_click=lambda _: self.on_request_permission() if self.on_request_permission else None,
                    )
                ]
            )

        if self.pending_count > 0:
            return ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Row(
                        expand=True,
                        spacing=10,
                        controls=[
                            ft.Container(
                                content=ft.Icon(ft.Icons.NOTIFICATIONS_ACTIVE, color=AppColors.PRIMARY_LIGHT, size=18),
                                bgcolor=ft.Colors.with_opacity(0.2, AppColors.PRIMARY),
                                border_radius=10,
                                padding=6,
                            ),
                            ft.Column(
                                spacing=2,
                                expand=True,
                                controls=[
                                    ft.Row(
                                        spacing=6,
                                        controls=[
                                            ft.Text("Thông báo mới", size=12, weight=ft.FontWeight.BOLD, color=AppColors.TEXT_PRIMARY),
                                            ft.Container(
                                                content=ft.Text(f"{self.pending_count}", size=10, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                                                bgcolor=AppColors.EXPENSE,
                                                border_radius=8,
                                                padding=ft.Padding.symmetric(horizontal=6, vertical=1),
                                            )
                                        ]
                                    ),
                                    ft.Text("Biến động số dư đang chờ bạn duyệt", size=11, color=AppColors.TEXT_MUTED, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                                ]
                            )
                        ]
                    ),
                    ft.FilledButton(
                        content=ft.Text("Duyệt ngay", size=11, weight=ft.FontWeight.BOLD),
                        style=ft.ButtonStyle(bgcolor=AppColors.PRIMARY),
                        on_click=lambda _: self.on_review_click() if self.on_review_click else None,
                    )
                ]
            )
        else:
            return ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Row(
                        expand=True,
                        spacing=8,
                        controls=[
                            ft.Container(
                                width=8,
                                height=8,
                                border_radius=4,
                                bgcolor=AppColors.INCOME,
                            ),
                            ft.Column(
                                spacing=1,
                                expand=True,
                                controls=[
                                    ft.Text("Bắt biến động số dư: Sẵn sàng", size=11, weight=ft.FontWeight.BOLD, color=AppColors.TEXT_PRIMARY),
                                    ft.Text("Sacombank, Cake, MoMo", size=10, color=AppColors.TEXT_MUTED, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                                ]
                            )
                        ]
                    ),
                    ft.TextButton(
                        content=ft.Text("Hộp thư", size=11, color=AppColors.PRIMARY_LIGHT),
                        on_click=lambda _: self.on_review_click() if self.on_review_click else None,
                    )
                ]
            )

