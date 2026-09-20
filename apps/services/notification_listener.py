from typing import Optional, List, Dict, Any
from apps.models.notification import BankNotification, ParseResult
from apps.models.transaction import Income, Expense
from apps.models.category import CategoryType
from apps.database.repositories import (
    BankNotificationRepository,
    CategoryRepository,
    IncomeRepository,
    ExpenseRepository
)
from apps.services.notification_parser import BankNotificationParser
from apps.core.events import EventBus, EVENT_NOTIFICATION_RECEIVED, EVENT_TRANSACTION_UPDATED

class NotificationService:
    def __init__(
        self,
        notif_repo: BankNotificationRepository,
        cat_repo: CategoryRepository,
        income_repo: IncomeRepository,
        expense_repo: ExpenseRepository
    ):
        self.notif_repo = notif_repo
        self.cat_repo = cat_repo
        self.income_repo = income_repo
        self.expense_repo = expense_repo
        self._processed_keys = set()

    def process_incoming_message(
        self,
        raw_message: str,
        sender_app: str = "",
        auto_approve: bool = False,
        notif_time: Optional[Any] = None,
        notif_id: Optional[Any] = None
    ) -> Optional[BankNotification]:
        """
        Parse raw notification message, match suggested category, and save to database.
        """
        parsed: ParseResult = BankNotificationParser.parse(raw_message, sender_app)
        if not parsed.is_valid:
            return None

        # Deduplication: Prevent duplicate ingestion of the exact same notification event
        # (e.g. if incoming_notifications.jsonl is polled twice before being truncated)
        event_key = f"{sender_app}_{notif_time}_{notif_id}_{raw_message}"
        if event_key in self._processed_keys:
            return None
        self._processed_keys.add(event_key)
        # Keep set bounded
        if len(self._processed_keys) > 500:
            self._processed_keys = set(list(self._processed_keys)[-200:])


        # Find matching category in database
        target_type = CategoryType.INCOME if parsed.transaction_type == "income" else CategoryType.EXPENSE
        categories = self.cat_repo.get_by_type(target_type)
        
        matched_cat_id = None
        matched_cat_name = parsed.suggested_category

        for c in categories:
            if c.name.lower() == parsed.suggested_category.lower():
                matched_cat_id = c.id
                matched_cat_name = c.name
                break
        
        if matched_cat_id is None and categories:
            # Fallback to first category of that type
            matched_cat_id = categories[0].id
            matched_cat_name = categories[0].name

        notif = BankNotification(
            bank_name=parsed.bank_name,
            raw_content=raw_message,
            received_at=parsed.transaction_time or "",
            amount=parsed.amount,
            transaction_type=parsed.transaction_type,
            detected_description=parsed.description,
            suggested_category_id=matched_cat_id,
            suggested_category_name=matched_cat_name,
            status="approved" if auto_approve else "pending"
        )

        notif_id = self.notif_repo.add(notif)
        notif.id = notif_id

        if auto_approve:
            tx_id = self.approve_notification(notif_id)
            notif.created_transaction_id = tx_id

        # Notify UI via EventBus
        EventBus.publish(EVENT_NOTIFICATION_RECEIVED, notif)
        return notif

    def approve_notification(self, notif_id: int, override_category_id: Optional[int] = None, override_desc: Optional[str] = None) -> Optional[int]:
        """
        Convert a pending bank notification into a real Income or Expense transaction.
        """
        notifs = self.notif_repo.get_all()
        target = next((n for n in notifs if n.id == notif_id), None)
        if not target:
            return None

        cat_id = override_category_id if override_category_id is not None else target.suggested_category_id
        desc = override_desc if override_desc is not None else target.detected_description
        date_str = target.received_at.split(" ")[0] if " " in target.received_at else target.received_at

        created_tx_id = None
        if target.transaction_type == "income":
            income = Income(
                amount=target.amount,
                date=date_str,
                description=desc,
                category_id=cat_id,
                source=target.bank_name
            )
            created_tx_id = self.income_repo.add(income)
        else:
            expense = Expense(
                amount=target.amount,
                date=date_str,
                description=desc,
                category_id=cat_id,
                is_essential=False,
                payment_method=target.bank_name
            )
            created_tx_id = self.expense_repo.add(expense)

        self.notif_repo.update_status(notif_id, "approved", created_tx_id)
        EventBus.publish(EVENT_TRANSACTION_UPDATED)
        return created_tx_id

    def discard_notification(self, notif_id: int) -> bool:
        """Mark notification as discarded"""
        res = self.notif_repo.update_status(notif_id, "discarded")
        EventBus.publish(EVENT_NOTIFICATION_RECEIVED)
        return res
