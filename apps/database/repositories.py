import sqlite3
from typing import List, Optional, Tuple, Dict, Any
from datetime import datetime
from apps.database.db import Database
from apps.models.category import Category, CategoryType
from apps.models.transaction import Income, Expense, Transaction
from apps.models.notification import BankNotification

class CategoryRepository:
    def __init__(self, db: Database):
        self.db = db

    def _row_to_model(self, row: sqlite3.Row) -> Category:
        return Category(
            id=row["id"],
            name=row["name"],
            description=row["description"] or "",
            type=CategoryType(row["type"]),
            is_active=bool(row["is_active"]),
            icon=row["icon"] or "category",
            color=row["color"] or "#6366F1",
        )

    def get_all(self, include_inactive: bool = False) -> List[Category]:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            if include_inactive:
                cursor.execute("SELECT * FROM categories ORDER BY name ASC")
            else:
                cursor.execute("SELECT * FROM categories WHERE is_active = 1 ORDER BY name ASC")
            return [self._row_to_model(r) for r in cursor.fetchall()]

    def get_by_id(self, category_id: int) -> Optional[Category]:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM categories WHERE id = ?", (category_id,))
            row = cursor.fetchone()
            return self._row_to_model(row) if row else None

    def get_by_type(self, cat_type: CategoryType) -> List[Category]:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM categories WHERE type = ? AND is_active = 1 ORDER BY name ASC",
                (int(cat_type),)
            )
            return [self._row_to_model(r) for r in cursor.fetchall()]

    def add(self, category: Category) -> int:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO categories (name, description, type, is_active, icon, color)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (category.name, category.description, int(category.type), 1 if category.is_active else 0, category.icon, category.color)
            )
            conn.commit()
            return cursor.lastrowid

    def update(self, category: Category) -> bool:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE categories 
                SET name = ?, description = ?, type = ?, is_active = ?, icon = ?, color = ?
                WHERE id = ?
                """,
                (category.name, category.description, int(category.type), 1 if category.is_active else 0, category.icon, category.color, category.id)
            )
            conn.commit()
            return cursor.rowcount > 0

    def delete(self, category_id: int) -> bool:
        # Soft delete
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE categories SET is_active = 0 WHERE id = ?", (category_id,))
            conn.commit()
            return cursor.rowcount > 0


class IncomeRepository:
    def __init__(self, db: Database):
        self.db = db

    def _row_to_model(self, row: sqlite3.Row) -> Income:
        cat = None
        if row["cat_id"] is not None:
            cat = Category(
                id=row["cat_id"],
                name=row["cat_name"],
                description=row["cat_desc"] or "",
                type=CategoryType.INCOME,
                is_active=bool(row["cat_active"]),
                icon=row["cat_icon"] or "category",
                color=row["cat_color"] or "#10B981"
            )
        return Income(
            id=row["id"],
            amount=row["amount"],
            date=row["date"],
            description=row["description"] or "",
            category_id=row["category_id"],
            source=row["source"] or "Khác",
            category=cat
        )

    def get_all(self, limit: int = 200) -> List[Income]:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT i.*, 
                       c.id as cat_id, c.name as cat_name, c.description as cat_desc, 
                       c.is_active as cat_active, c.icon as cat_icon, c.color as cat_color
                FROM incomes i
                LEFT JOIN categories c ON i.category_id = c.id
                ORDER BY i.date DESC, i.id DESC
                LIMIT ?
                """,
                (limit,)
            )
            return [self._row_to_model(r) for r in cursor.fetchall()]

    def get_by_date_range(self, start_date: str, end_date: str) -> List[Income]:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT i.*, 
                       c.id as cat_id, c.name as cat_name, c.description as cat_desc, 
                       c.is_active as cat_active, c.icon as cat_icon, c.color as cat_color
                FROM incomes i
                LEFT JOIN categories c ON i.category_id = c.id
                WHERE i.date BETWEEN ? AND ?
                ORDER BY i.date DESC, i.id DESC
                """,
                (start_date, end_date)
            )
            return [self._row_to_model(r) for r in cursor.fetchall()]

    def add(self, income: Income) -> int:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO incomes (amount, date, description, category_id, source)
                VALUES (?, ?, ?, ?, ?)
                """,
                (income.amount, income.date, income.description, income.category_id, income.source)
            )
            conn.commit()
            return cursor.lastrowid

    def update(self, income: Income) -> bool:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE incomes
                SET amount = ?, date = ?, description = ?, category_id = ?, source = ?
                WHERE id = ?
                """,
                (income.amount, income.date, income.description, income.category_id, income.source, income.id)
            )
            conn.commit()
            return cursor.rowcount > 0

    def delete(self, income_id: int) -> bool:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM incomes WHERE id = ?", (income_id,))
            conn.commit()
            return cursor.rowcount > 0

    def get_total_for_month(self, year: int, month: int) -> float:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            month_str = f"{month:02d}"
            cursor.execute(
                """
                SELECT COALESCE(SUM(amount), 0)
                FROM incomes
                WHERE strftime('%Y', date) = ? AND strftime('%m', date) = ?
                """,
                (str(year), month_str)
            )
            return float(cursor.fetchone()[0])


class ExpenseRepository:
    def __init__(self, db: Database):
        self.db = db

    def _row_to_model(self, row: sqlite3.Row) -> Expense:
        cat = None
        if row["cat_id"] is not None:
            cat = Category(
                id=row["cat_id"],
                name=row["cat_name"],
                description=row["cat_desc"] or "",
                type=CategoryType.EXPENSE,
                is_active=bool(row["cat_active"]),
                icon=row["cat_icon"] or "category",
                color=row["cat_color"] or "#EF4444"
            )
        return Expense(
            id=row["id"],
            amount=row["amount"],
            date=row["date"],
            description=row["description"] or "",
            category_id=row["category_id"],
            is_essential=bool(row["is_essential"]),
            payment_method=row["payment_method"] or "Chuyển khoản",
            category=cat
        )

    def get_all(self, limit: int = 200) -> List[Expense]:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT e.*, 
                       c.id as cat_id, c.name as cat_name, c.description as cat_desc, 
                       c.is_active as cat_active, c.icon as cat_icon, c.color as cat_color
                FROM expenses e
                LEFT JOIN categories c ON e.category_id = c.id
                ORDER BY e.date DESC, e.id DESC
                LIMIT ?
                """,
                (limit,)
            )
            return [self._row_to_model(r) for r in cursor.fetchall()]

    def get_by_date_range(self, start_date: str, end_date: str) -> List[Expense]:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT e.*, 
                       c.id as cat_id, c.name as cat_name, c.description as cat_desc, 
                       c.is_active as cat_active, c.icon as cat_icon, c.color as cat_color
                FROM expenses e
                LEFT JOIN categories c ON e.category_id = c.id
                WHERE e.date BETWEEN ? AND ?
                ORDER BY e.date DESC, e.id DESC
                """,
                (start_date, end_date)
            )
            return [self._row_to_model(r) for r in cursor.fetchall()]

    def add(self, expense: Expense) -> int:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO expenses (amount, date, description, category_id, is_essential, payment_method)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (expense.amount, expense.date, expense.description, expense.category_id, 1 if expense.is_essential else 0, expense.payment_method)
            )
            conn.commit()
            return cursor.lastrowid

    def update(self, expense: Expense) -> bool:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE expenses
                SET amount = ?, date = ?, description = ?, category_id = ?, is_essential = ?, payment_method = ?
                WHERE id = ?
                """,
                (expense.amount, expense.date, expense.description, expense.category_id, 1 if expense.is_essential else 0, expense.payment_method, expense.id)
            )
            conn.commit()
            return cursor.rowcount > 0

    def delete(self, expense_id: int) -> bool:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
            conn.commit()
            return cursor.rowcount > 0

    def get_total_for_month(self, year: int, month: int) -> float:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            month_str = f"{month:02d}"
            cursor.execute(
                """
                SELECT COALESCE(SUM(amount), 0)
                FROM expenses
                WHERE strftime('%Y', date) = ? AND strftime('%m', date) = ?
                """,
                (str(year), month_str)
            )
            return float(cursor.fetchone()[0])

    def get_totals_grouped_by_category(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT c.name as category_name, c.color as category_color, c.icon as category_icon,
                       COALESCE(SUM(e.amount), 0) as total_amount
                FROM expenses e
                LEFT JOIN categories c ON e.category_id = c.id
                WHERE e.date BETWEEN ? AND ?
                GROUP BY e.category_id
                HAVING total_amount > 0
                ORDER BY total_amount DESC
                """,
                (start_date, end_date)
            )
            return [
                {
                    "name": row["category_name"] or "Chưa phân loại",
                    "color": row["category_color"] or "#94A3B8",
                    "icon": row["category_icon"] or "category",
                    "total": float(row["total_amount"]),
                }
                for row in cursor.fetchall()
            ]


class BankNotificationRepository:
    def __init__(self, db: Database):
        self.db = db

    def _row_to_model(self, row: sqlite3.Row) -> BankNotification:
        return BankNotification(
            id=row["id"],
            bank_name=row["bank_name"],
            raw_content=row["raw_content"],
            received_at=row["received_at"],
            amount=row["amount"],
            transaction_type=row["transaction_type"],
            detected_description=row["detected_description"] or "",
            suggested_category_id=row["suggested_category_id"],
            suggested_category_name=row["suggested_category_name"] or "Chưa phân loại",
            status=row["status"],
            created_transaction_id=row["created_transaction_id"]
        )

    def get_all(self, status: Optional[str] = None) -> List[BankNotification]:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            if status:
                cursor.execute("SELECT * FROM bank_notifications WHERE status = ? ORDER BY id DESC", (status,))
            else:
                cursor.execute("SELECT * FROM bank_notifications ORDER BY id DESC")
            return [self._row_to_model(r) for r in cursor.fetchall()]

    def get_pending_count(self) -> int:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM bank_notifications WHERE status = 'pending'")
            return cursor.fetchone()[0]

    def is_duplicate(
        self,
        amount: float,
        transaction_type: str,
        description: str,
        raw_content: str,
        bank_name: Optional[str] = None
    ) -> bool:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()

            # 1. Exact raw_content match among non-discarded notifications
            cursor.execute(
                "SELECT id FROM bank_notifications WHERE raw_content = ? AND status != 'discarded' LIMIT 1",
                (raw_content,)
            )
            if cursor.fetchone():
                return True

            desc_clean = (description or "").strip()
            # 2. Check pending notifications with exact same amount, transaction type, and description
            if len(desc_clean) >= 4:
                cursor.execute(
                    """
                    SELECT id FROM bank_notifications 
                    WHERE amount = ? AND transaction_type = ? AND detected_description = ? AND status = 'pending'
                    LIMIT 1
                    """,
                    (amount, transaction_type, desc_clean)
                )
                if cursor.fetchone():
                    return True

            # 3. Match identical amount + bank + transaction_type for pending notifications if description is similar
            if bank_name:
                cursor.execute(
                    """
                    SELECT id, detected_description FROM bank_notifications
                    WHERE bank_name = ? AND amount = ? AND transaction_type = ? AND status = 'pending'
                    LIMIT 5
                    """,
                    (bank_name, amount, transaction_type)
                )
                rows = cursor.fetchall()
                for r in rows:
                    existing_desc = (r["detected_description"] or "").strip().lower()
                    new_desc = desc_clean.lower()
                    if existing_desc == new_desc:
                        return True
                    if len(existing_desc) >= 6 and len(new_desc) >= 6:
                        if existing_desc in new_desc or new_desc in existing_desc:
                            return True

            return False

    def add(self, n: BankNotification) -> int:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO bank_notifications 
                (bank_name, raw_content, received_at, amount, transaction_type, detected_description, suggested_category_id, suggested_category_name, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (n.bank_name, n.raw_content, n.received_at, n.amount, n.transaction_type, n.detected_description, n.suggested_category_id, n.suggested_category_name, n.status)
            )
            conn.commit()
            return cursor.lastrowid

    def update_status(self, notif_id: int, status: str, created_transaction_id: Optional[int] = None) -> bool:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE bank_notifications
                SET status = ?, created_transaction_id = ?
                WHERE id = ?
                """,
                (status, created_transaction_id, notif_id)
            )
            conn.commit()
            return cursor.rowcount > 0

    def delete(self, notif_id: int) -> bool:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM bank_notifications WHERE id = ?", (notif_id,))
            conn.commit()
            return cursor.rowcount > 0


class BudgetRepository:
    def __init__(self, db: Database):
        self.db = db

    def get_budget(self, year: int, month: int, default_limit: float = 10000000.0) -> float:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT budget_limit FROM monthly_budgets WHERE year = ? AND month = ?",
                (year, month)
            )
            row = cursor.fetchone()
            return float(row[0]) if row else default_limit

    def set_budget(self, year: int, month: int, budget_limit: float) -> bool:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO monthly_budgets (year, month, budget_limit)
                VALUES (?, ?, ?)
                ON CONFLICT(year, month) DO UPDATE SET budget_limit = excluded.budget_limit
                """,
                (year, month, budget_limit)
            )
            conn.commit()
            return cursor.rowcount > 0
