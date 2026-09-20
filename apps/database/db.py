import sqlite3
from pathlib import Path
from typing import Optional
from apps.core.config import DB_PATH, DEFAULT_INCOME_CATEGORIES, DEFAULT_EXPENSE_CATEGORIES

class Database:
    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or DB_PATH
        self.init_db()

    def get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def init_db(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # 1. Categories table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    description TEXT,
                    type INTEGER NOT NULL, -- 0: Income, 1: Expense
                    is_active INTEGER NOT NULL DEFAULT 1,
                    icon TEXT DEFAULT 'category',
                    color TEXT DEFAULT '#6366F1'
                )
            """)

            # 2. Incomes table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS incomes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    amount REAL NOT NULL,
                    date TEXT NOT NULL,
                    description TEXT,
                    category_id INTEGER,
                    source TEXT,
                    FOREIGN KEY(category_id) REFERENCES categories(id) ON DELETE SET NULL
                )
            """)

            # 3. Expenses table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS expenses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    amount REAL NOT NULL,
                    date TEXT NOT NULL,
                    description TEXT,
                    category_id INTEGER,
                    is_essential INTEGER NOT NULL DEFAULT 0,
                    payment_method TEXT,
                    FOREIGN KEY(category_id) REFERENCES categories(id) ON DELETE SET NULL
                )
            """)

            # 4. Bank Notifications table (Pending Inbox)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS bank_notifications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    bank_name TEXT NOT NULL,
                    raw_content TEXT NOT NULL,
                    received_at TEXT NOT NULL,
                    amount REAL NOT NULL,
                    transaction_type TEXT NOT NULL,
                    detected_description TEXT,
                    suggested_category_id INTEGER,
                    suggested_category_name TEXT,
                    status TEXT NOT NULL DEFAULT 'pending',
                    created_transaction_id INTEGER,
                    FOREIGN KEY(suggested_category_id) REFERENCES categories(id) ON DELETE SET NULL
                )
            """)

            # 5. Monthly Budgets table (Định mức chi tiêu)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS monthly_budgets (
                    year INTEGER NOT NULL,
                    month INTEGER NOT NULL,
                    budget_limit REAL NOT NULL,
                    PRIMARY KEY (year, month)
                )
            """)

            conn.commit()

            # Seed default categories if empty
            cursor.execute("SELECT COUNT(*) FROM categories")
            if cursor.fetchone()[0] == 0:
                self._seed_default_categories(cursor)
                conn.commit()

            # Clean up any existing duplicate pending notifications (keeping oldest unique row)
            cursor.execute("""
                DELETE FROM bank_notifications 
                WHERE status = 'pending' AND id NOT IN (
                    SELECT MIN(id) 
                    FROM bank_notifications 
                    WHERE status = 'pending' 
                    GROUP BY amount, transaction_type, COALESCE(detected_description, '')
                )
            """)
            conn.commit()

    def _seed_default_categories(self, cursor: sqlite3.Cursor):
        for item in DEFAULT_INCOME_CATEGORIES:
            cursor.execute(
                "INSERT INTO categories (name, description, type, is_active, icon, color) VALUES (?, ?, 0, 1, ?, ?)",
                (item["name"], item["description"], item["icon"], item["color"])
            )
        for item in DEFAULT_EXPENSE_CATEGORIES:
            cursor.execute(
                "INSERT INTO categories (name, description, type, is_active, icon, color) VALUES (?, ?, 1, 1, ?, ?)",
                (item["name"], item["description"], item["icon"], item["color"])
            )
