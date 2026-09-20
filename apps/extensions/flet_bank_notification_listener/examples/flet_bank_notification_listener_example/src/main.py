import flet as ft

from flet_bank_notification_listener import FletBankNotificationListener


def main(page: ft.Page):
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    page.add(

                ft.Container(height=150, width=300, alignment = ft.Alignment.CENTER, bgcolor=ft.Colors.PURPLE_200, content=FletBankNotificationListener(
                    tooltip="My new FletBankNotificationListener Control tooltip",
                    value = "My new FletBankNotificationListener Flet Control",
                ),),

    )


ft.run(main)
