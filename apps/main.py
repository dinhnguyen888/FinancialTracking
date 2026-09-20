import sys
import json
import types
import asyncio
from pathlib import Path
import flet as ft

# Ensure self and extensions directories are in sys.path
CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

# Map 'apps' to current directory when packaged into mobile APK
if "apps" not in sys.modules:
    apps_mod = types.ModuleType("apps")
    apps_mod.__path__ = [str(CURRENT_DIR)]
    apps_mod.__file__ = str(CURRENT_DIR / "__init__.py")
    sys.modules["apps"] = apps_mod

EXT_PATH = CURRENT_DIR / "extensions" / "flet_bank_notification_listener" / "src"
if str(EXT_PATH) not in sys.path:
    sys.path.insert(0, str(EXT_PATH))

try:
    from flet_bank_notification_listener import FletBankNotificationListener
except ImportError:
    FletBankNotificationListener = None

from apps.core.config import APP_NAME, DATA_DIR
from apps.core.theme import AppColors, get_app_theme, format_currency
from apps.core.events import EventBus, EVENT_NOTIFICATION_RECEIVED, EVENT_TRANSACTION_UPDATED
from apps.database.db import Database
from apps.database.repositories import (
    CategoryRepository,
    IncomeRepository,
    ExpenseRepository,
    BankNotificationRepository,
    BudgetRepository,
)
from apps.models.notification import BankNotification
from apps.services.notification_listener import NotificationService
from apps.ui.views import (
    DashboardView,
    TransactionsView,
    AddTransactionBottomSheet,
    PendingNotificationsView,
    ReportsView,
    CategoriesView,
)

def main(page: ft.Page):
    page.title = APP_NAME
    page.theme_mode = ft.ThemeMode.DARK
    page.theme = get_app_theme()
    page.bgcolor = AppColors.BG_DARK
    page.padding = 0

    # Mobile frame dimensions for desktop preview (ignored on mobile)
    try:
        page.window.width = 412
        page.window.height = 860
        page.window.min_width = 360
        page.window.min_height = 640
    except Exception:
        pass

    # 1. Initialize Database & Repositories
    db = Database()
    cat_repo = CategoryRepository(db)
    income_repo = IncomeRepository(db)
    expense_repo = ExpenseRepository(db)
    notif_repo = BankNotificationRepository(db)
    budget_repo = BudgetRepository(db)

    # 2. Notification Service
    notif_service = NotificationService(notif_repo, cat_repo, income_repo, expense_repo)

    # 3. Dynamic Inbox Badge
    def update_inbox_badge():
        try:
            pending_count = len(notif_repo.get_all(status="pending"))
            if pending_count > 0:
                nav_bar.destinations[2].badge = ft.Badge(
                    label=str(pending_count),
                    bgcolor=AppColors.ERROR,
                )
            else:
                nav_bar.destinations[2].badge = None
            page.update()
        except Exception:
            pass

    # 4. Floating SnackBar for live bank transactions
    def show_live_transaction_snack(notif: BankNotification):
        try:
            sign = "+" if notif.transaction_type == "income" else "-"
            amt_formatted = format_currency(notif.amount)
            desc_short = notif.detected_description[:30] if notif.detected_description else "Giao dịch ngân hàng"
            
            snack = ft.SnackBar(
                content=ft.Row(
                    spacing=10,
                    controls=[
                        ft.Icon(
                            ft.Icons.NOTIFICATIONS_ACTIVE,
                            color=AppColors.INCOME if notif.transaction_type == "income" else AppColors.EXPENSE,
                            size=24
                        ),
                        ft.Column(
                            spacing=2,
                            tight=True,
                            controls=[
                                ft.Text(
                                    f"Biến động: {notif.bank_name}",
                                    weight=ft.FontWeight.BOLD,
                                    size=13,
                                    color=ft.Colors.WHITE
                                ),
                                ft.Text(
                                    f"{sign}{amt_formatted} • {desc_short}",
                                    size=12,
                                    color=ft.Colors.WHITE70
                                ),
                            ]
                        )
                    ]
                ),
                action="Xem ngay",
                action_color=AppColors.PRIMARY_LIGHT,
                on_action=lambda _: navigate_to_tab(2),
                bgcolor=AppColors.CARD_DARK,
                duration=5000,
            )
            page.overlay.append(snack)
            snack.open = True
            page.update()
        except Exception:
            pass

    # 5. Native Android Bank Notification Watcher
    def check_incoming_notifications():
        candidate_paths = [
            DATA_DIR / "incoming_notifications.jsonl",
            DATA_DIR.parent / "incoming_notifications.jsonl",
            Path.home() / "incoming_notifications.jsonl",
            Path("/storage/emulated/0/Android/data/com.cashflowtracking.cashflowtracking/files/incoming_notifications.jsonl"),
            Path("/sdcard/Android/data/com.cashflowtracking.cashflowtracking/files/incoming_notifications.jsonl"),
        ]
        newly_processed = []
        for p in candidate_paths:
            if p.exists() and p.is_file() and p.stat().st_size > 0:
                try:
                    with open(p, "r", encoding="utf-8") as f:
                        lines = f.readlines()
                    with open(p, "w", encoding="utf-8") as f:
                        f.write("")
                    
                    for line in lines:
                        if not line.strip():
                            continue
                        data = json.loads(line)
                        pkg = data.get("package", "")
                        title = data.get("title", "")
                        text = data.get("text", "")
                        notif_time = data.get("time")
                        notif_id = data.get("id")
                        full_msg = f"{title}\n{text}".strip() if title else text
                        saved_notif = notif_service.process_incoming_message(
                            raw_message=full_msg,
                            sender_app=pkg,
                            notif_time=notif_time,
                            notif_id=notif_id
                        )
                        if saved_notif:
                            newly_processed.append(saved_notif)
                except Exception:
                    pass

        if newly_processed:
            update_inbox_badge()
            show_live_transaction_snack(newly_processed[-1])
            # Refresh currently visible view
            current_view = views[nav_bar.selected_index]
            if hasattr(current_view, "refresh_data"):
                current_view.refresh_data()
            page.update()

    # Process any backlog on startup
    check_incoming_notifications()

    # Continuous background polling
    async def poll_notifications():
        while True:
            await asyncio.sleep(2)
            check_incoming_notifications()

    asyncio.create_task(poll_notifications())

    # 6. Handlers for navigation & dialogs
    def open_add_transaction_modal(existing_tx=None):
        sheet = AddTransactionBottomSheet(
            income_repo=income_repo,
            expense_repo=expense_repo,
            cat_repo=cat_repo,
            existing_tx=existing_tx,
            on_saved=lambda: page.update(),
        )
        page.show_dialog(sheet)

    def navigate_to_tab(index: int):
        nav_bar.selected_index = index
        on_nav_change(None)

    # 7. Create Views
    view_dashboard = DashboardView(
        income_repo=income_repo,
        expense_repo=expense_repo,
        notif_repo=notif_repo,
        budget_repo=budget_repo,
        on_navigate_tab=navigate_to_tab,
        on_open_add=lambda: open_add_transaction_modal(None),
        on_edit_tx=open_add_transaction_modal,
    )

    view_transactions = TransactionsView(
        income_repo=income_repo,
        expense_repo=expense_repo,
        cat_repo=cat_repo,
        on_open_add=lambda: open_add_transaction_modal(None),
        on_edit_tx=open_add_transaction_modal,
    )

    view_notifications = PendingNotificationsView(
        notif_service=notif_service,
        notif_repo=notif_repo,
        cat_repo=cat_repo,
        on_navigate_dashboard=lambda: navigate_to_tab(0),
    )

    view_reports = ReportsView(
        income_repo=income_repo,
        expense_repo=expense_repo,
        cat_repo=cat_repo,
    )

    view_categories = CategoriesView(
        cat_repo=cat_repo,
    )

    views = [
        view_dashboard,
        view_transactions,
        view_notifications,
        view_reports,
        view_categories,
    ]

    # Content Container
    main_content = ft.Container(
        content=views[0],
        expand=True,
    )

    def on_nav_change(e):
        selected_idx = nav_bar.selected_index
        main_content.content = views[selected_idx]
        if hasattr(views[selected_idx], "refresh_data"):
            views[selected_idx].refresh_data()
        update_inbox_badge()
        page.update()

    # 8. Mobile Navigation Bar (configured directly on page for proper Scaffold layout)
    nav_bar = ft.NavigationBar(
        selected_index=0,
        bgcolor=AppColors.SURFACE_DARK,
        indicator_color=AppColors.PRIMARY,
        destinations=[
            ft.NavigationBarDestination(icon=ft.Icons.DASHBOARD_OUTLINED, selected_icon=ft.Icons.DASHBOARD, label="Tổng quan"),
            ft.NavigationBarDestination(icon=ft.Icons.RECEIPT_LONG_OUTLINED, selected_icon=ft.Icons.RECEIPT_LONG, label="Giao dịch"),
            ft.NavigationBarDestination(icon=ft.Icons.INBOX_OUTLINED, selected_icon=ft.Icons.INBOX, label="Hộp thư"),
            ft.NavigationBarDestination(icon=ft.Icons.DONUT_LARGE_OUTLINED, selected_icon=ft.Icons.DONUT_LARGE, label="Báo cáo"),
            ft.NavigationBarDestination(icon=ft.Icons.GRID_VIEW_OUTLINED, selected_icon=ft.Icons.GRID_VIEW, label="Danh mục"),
        ],
        on_change=on_nav_change,
    )

    # Subscribe to EventBus updates
    EventBus.subscribe(EVENT_NOTIFICATION_RECEIVED, lambda *_: update_inbox_badge())
    EventBus.subscribe(EVENT_TRANSACTION_UPDATED, lambda *_: update_inbox_badge())

    page.navigation_bar = nav_bar
    page.add(main_content)

    # Initial badge update
    update_inbox_badge()

    # 9. First-launch Permission Prompt Check
    def check_notification_permission_on_launch():
        candidate_flags = [
            DATA_DIR / "notification_permission_enabled.flag",
            DATA_DIR.parent / "notification_permission_enabled.flag",
            Path.home() / "notification_permission_enabled.flag",
            Path("/storage/emulated/0/Android/data/com.cashflowtracking.cashflowtracking/files/notification_permission_enabled.flag"),
            Path("/sdcard/Android/data/com.cashflowtracking.cashflowtracking/files/notification_permission_enabled.flag"),
        ]
        is_granted = any(p.exists() for p in candidate_flags)
        if not is_granted:
            def on_grant(_):
                try:
                    page.pop_dialog()
                except Exception:
                    pass
                page.launch_url("cashflow://settings/notifications")

            def on_later(_):
                try:
                    page.pop_dialog()
                except Exception:
                    pass

            perm_dlg = ft.AlertDialog(
                modal=True,
                title=ft.Row(
                    spacing=10,
                    controls=[
                        ft.Icon(ft.Icons.SECURITY_ROUNDED, color=AppColors.PRIMARY, size=26),
                        ft.Text("Cấp quyền Thông báo", size=18, weight=ft.FontWeight.BOLD, color=AppColors.TEXT_PRIMARY),
                    ]
                ),
                content=ft.Column(
                    spacing=12,
                    tight=True,
                    controls=[
                        ft.Text(
                            "Để ứng dụng tự động nhận diện biến động số dư khi bạn chuyển khoản hoặc nhận tiền (Sacombank, Cake, MoMo, Vietcombank, MB...), vui lòng cấp quyền Đọc thông báo.",
                            size=13,
                            color=AppColors.TEXT_SECONDARY,
                        ),
                        ft.Container(
                            bgcolor=AppColors.CARD_DARK,
                            padding=12,
                            border_radius=12,
                            content=ft.Column(
                                spacing=6,
                                controls=[
                                    ft.Text("Các bước kích hoạt nhanh:", size=12, weight=ft.FontWeight.BOLD, color=AppColors.PRIMARY_LIGHT),
                                    ft.Text("1. Nhấn nút 'Cấp quyền ngay'", size=12, color=AppColors.TEXT_MUTED),
                                    ft.Text("2. Chọn ứng dụng CashflowTracking", size=12, color=AppColors.TEXT_MUTED),
                                    ft.Text("3. Bật gạt Cho phép truy cập thông báo", size=12, color=AppColors.TEXT_MUTED),
                                ]
                            )
                        )
                    ]
                ),
                actions=[
                    ft.TextButton("Để sau", on_click=on_later),
                    ft.ElevatedButton(
                        "Cấp quyền ngay",
                        icon=ft.Icons.CHECK_CIRCLE,
                        bgcolor=AppColors.PRIMARY,
                        color=ft.Colors.WHITE,
                        on_click=on_grant,
                    ),
                ],
                actions_alignment=ft.MainAxisAlignment.END,
            )
            page.show_dialog(perm_dlg)

    # Run permission check shortly after UI mounts
    async def delayed_permission_check():
        await asyncio.sleep(0.8)
        check_notification_permission_on_launch()

    asyncio.create_task(delayed_permission_check())

if __name__ == "__main__":
    ft.run(main)
