import flet as ft
from typing import Callable
from apps.core.theme import AppColors

class MobileNumpad(ft.Container):
    def __init__(self, on_key: Callable[[str], None], on_backspace: Callable[[], None], on_clear: Callable[[], None]):
        self.on_key = on_key
        self.on_backspace = on_backspace
        self.on_clear = on_clear

        keys = [
            ["1", "2", "3"],
            ["4", "5", "6"],
            ["7", "8", "9"],
            ["000", "0", "⌫"]
        ]

        rows = []
        for row_keys in keys:
            btn_row = []
            for k in row_keys:
                if k == "⌫":
                    btn = ft.Container(
                        content=ft.Icon(ft.Icons.BACKSPACE_OUTLINED, size=20, color=AppColors.TEXT_PRIMARY),
                        alignment=ft.Alignment(0, 0),
                        height=52,
                        expand=True,
                        bgcolor=AppColors.CARD_DARK,
                        border_radius=12,
                        on_click=lambda _, fn=self.on_backspace: fn(),
                        ink=True,
                    )
                else:
                    btn = ft.Container(
                        content=ft.Text(k, size=20, weight=ft.FontWeight.BOLD, color=AppColors.TEXT_PRIMARY),
                        alignment=ft.Alignment(0, 0),
                        height=52,
                        expand=True,
                        bgcolor=AppColors.CARD_DARK,
                        border_radius=12,
                        on_click=lambda _, key=k: self.on_key(key),
                        ink=True,
                    )
                btn_row.append(btn)
            rows.append(ft.Row(spacing=8, controls=btn_row))

        super().__init__(
            content=ft.Column(spacing=8, controls=rows),
            padding=ft.Padding.all(6),
        )
