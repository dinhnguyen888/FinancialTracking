import flet as ft
from apps.core.theme import AppColors
from apps.core.events import EventBus, EVENT_CATEGORY_UPDATED, EVENT_TRANSACTION_UPDATED
from apps.models.category import Category, CategoryType
from apps.database.repositories import CategoryRepository
from apps.ui.components.transaction_card import ICON_MAP

AVAILABLE_ICONS = [
    ("restaurant", "Ăn uống", ft.Icons.RESTAURANT),
    ("directions_car", "Đi lại", ft.Icons.DIRECTIONS_CAR),
    ("home", "Nhà cửa", ft.Icons.HOME),
    ("sports_esports", "Giải trí", ft.Icons.SPORTS_ESPORTS),
    ("favorite", "Sức khỏe", ft.Icons.FAVORITE),
    ("shopping_bag", "Mua sắm", ft.Icons.SHOPPING_BAG),
    ("school", "Giáo dục", ft.Icons.SCHOOL),
    ("receipt_long", "Hóa đơn", ft.Icons.RECEIPT_LONG),
    ("work", "Lương", ft.Icons.WORK),
    ("card_giftcard", "Thưởng", ft.Icons.CARD_GIFTCARD),
    ("trending_up", "Đầu tư", ft.Icons.TRENDING_UP),
    ("laptop_chromebook", "Freelance", ft.Icons.LAPTOP_CHROMEBOOK),
    ("payments", "Thanh toán", ft.Icons.PAYMENTS),
    ("category", "Khác", ft.Icons.CATEGORY),
]

AVAILABLE_COLORS = [
    "#EF4444", "#F97316", "#F59E0B", "#10B981", "#06B6D4", "#3B82F6", "#6366F1", "#8B5CF6", "#EC4899", "#64748B"
]

class CategoriesView(ft.Container):
    def __init__(self, cat_repo: CategoryRepository):
        self.cat_repo = cat_repo
        self.current_type = CategoryType.EXPENSE
        self.list_container = ft.Column(spacing=10)

        super().__init__(
            content=self._build_layout(),
            expand=True,
            padding=ft.Padding.only(left=16, right=16, top=10, bottom=16),
        )

        EventBus.subscribe(EVENT_CATEGORY_UPDATED, self.refresh_data)
        self.refresh_data()

    def _build_layout(self) -> ft.Control:
        return ft.Column(
            spacing=14,
            expand=True,
            controls=[
                # Header & Add Button
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Text("Quản lý Danh mục", size=20, weight=ft.FontWeight.BOLD, color=AppColors.TEXT_PRIMARY),
                        ft.FilledButton(
                            content=ft.Row(
                                spacing=4,
                                controls=[
                                    ft.Icon(ft.Icons.ADD, size=16, color=ft.Colors.WHITE),
                                    ft.Text("Thêm", size=12, weight=ft.FontWeight.BOLD),
                                ]
                            ),
                            style=ft.ButtonStyle(bgcolor=AppColors.PRIMARY),
                            on_click=lambda _: self._show_add_category_dialog(),
                        )
                    ]
                ),

                # Type Selector Tabs
                ft.Row(
                    spacing=8,
                    controls=[
                        self._type_tab("Danh mục Chi tiêu", CategoryType.EXPENSE),
                        self._type_tab("Danh mục Thu nhập", CategoryType.INCOME),
                    ]
                ),

                # Scrollable list
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

    def _type_tab(self, label: str, cat_type: CategoryType) -> ft.Control:
        is_active = self.current_type == cat_type
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
            on_click=lambda _, t=cat_type: self._set_type(t),
            ink=True,
            border=ft.Border.all(1, AppColors.PRIMARY if is_active else ft.Colors.with_opacity(0.1, AppColors.BORDER_DARK)),
        )

    def _set_type(self, cat_type: CategoryType):
        self.current_type = cat_type
        self.content.controls[1] = ft.Row(
            spacing=8,
            controls=[
                self._type_tab("Danh mục Chi tiêu", CategoryType.EXPENSE),
                self._type_tab("Danh mục Thu nhập", CategoryType.INCOME),
            ]
        )
        self.refresh_data()

    def refresh_data(self, *args, **kwargs):
        try:
            cats = self.cat_repo.get_by_type(self.current_type)
            self.list_container.controls.clear()

            for cat in cats:
                card = self._build_category_card(cat)
                self.list_container.controls.append(card)

            if self.page:
                self.update()
        except Exception:
            pass

    def _build_category_card(self, cat: Category) -> ft.Control:
        flet_icon = ICON_MAP.get(cat.icon, ft.Icons.CATEGORY)
        return ft.Container(
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Row(
                        spacing=12,
                        controls=[
                            ft.Container(
                                content=ft.Icon(flet_icon, color=cat.color, size=20),
                                bgcolor=ft.Colors.with_opacity(0.15, cat.color),
                                border_radius=12,
                                padding=8,
                            ),
                            ft.Column(
                                spacing=2,
                                controls=[
                                    ft.Text(cat.name, size=14, weight=ft.FontWeight.W_600, color=AppColors.TEXT_PRIMARY),
                                    ft.Text(cat.description or "Không có mô tả", size=11, color=AppColors.TEXT_MUTED),
                                ]
                            )
                        ]
                    ),
                    ft.Row(
                        spacing=4,
                        controls=[
                            ft.IconButton(
                                icon=ft.Icons.EDIT_OUTLINED,
                                icon_size=18,
                                icon_color=AppColors.TEXT_MUTED,
                                tooltip="Sửa danh mục",
                                on_click=lambda _, c=cat: self._show_edit_category_dialog(c),
                            ),
                            ft.IconButton(
                                icon=ft.Icons.DELETE_OUTLINE,
                                icon_size=18,
                                icon_color=AppColors.EXPENSE,
                                tooltip="Xóa danh mục",
                                on_click=lambda _, c=cat: self._delete_category(c),
                            ),
                        ]
                    )
                ]
            ),
            bgcolor=AppColors.CARD_DARK,
            border_radius=14,
            padding=12,
            border=ft.Border.all(1, ft.Colors.with_opacity(0.12, AppColors.BORDER_DARK)),
        )

    def _show_add_category_dialog(self):
        self._show_category_dialog(None)

    def _show_edit_category_dialog(self, cat: Category):
        self._show_category_dialog(cat)

    def _show_category_dialog(self, existing_cat: Category = None):
        name_field = ft.TextField(
            value=existing_cat.name if existing_cat else "",
            label="Tên danh mục",
            border_radius=12,
            bgcolor=AppColors.CARD_DARK,
        )
        desc_field = ft.TextField(
            value=existing_cat.description if existing_cat else "",
            label="Mô tả",
            border_radius=12,
            bgcolor=AppColors.CARD_DARK,
        )

        selected_icon = existing_cat.icon if existing_cat else "category"
        selected_color = existing_cat.color if existing_cat else "#6366F1"

        def save_cat(e):
            if not name_field.value.strip():
                return
            if existing_cat:
                existing_cat.name = name_field.value.strip()
                existing_cat.description = desc_field.value.strip()
                existing_cat.icon = selected_icon
                existing_cat.color = selected_color
                self.cat_repo.update(existing_cat)
            else:
                new_cat = Category(
                    name=name_field.value.strip(),
                    description=desc_field.value.strip(),
                    type=self.current_type,
                    icon=selected_icon,
                    color=selected_color
                )
                self.cat_repo.add(new_cat)

            dialog.open = False
            self.page.update()
            EventBus.publish(EVENT_CATEGORY_UPDATED)

        dialog = ft.AlertDialog(
            title=ft.Text("Chỉnh sửa danh mục" if existing_cat else "Thêm danh mục mới", weight=ft.FontWeight.BOLD),
            content=ft.Column(
                tight=True,
                spacing=12,
                controls=[
                    name_field,
                    desc_field,
                ]
            ),
            actions=[
                ft.TextButton("Hủy", on_click=lambda _: self._close_dialog(dialog)),
                ft.FilledButton("Lưu", on_click=save_cat, style=ft.ButtonStyle(bgcolor=AppColors.PRIMARY)),
            ],
            bgcolor=AppColors.BG_DARK,
        )
        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()

    def _close_dialog(self, dialog):
        dialog.open = False
        self.page.update()

    def _delete_category(self, cat: Category):
        self.cat_repo.delete(cat.id)
        EventBus.publish(EVENT_CATEGORY_UPDATED)
