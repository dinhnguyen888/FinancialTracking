from typing import Callable, Dict, List
import logging

class EventBus:
    _listeners: Dict[str, List[Callable]] = {}

    @classmethod
    def subscribe(cls, event_name: str, callback: Callable):
        if event_name not in cls._listeners:
            cls._listeners[event_name] = []
        if callback not in cls._listeners[event_name]:
            cls._listeners[event_name].append(callback)

    @classmethod
    def unsubscribe(cls, event_name: str, callback: Callable):
        if event_name in cls._listeners and callback in cls._listeners[event_name]:
            cls._listeners[event_name].remove(callback)

    @classmethod
    def publish(cls, event_name: str, *args, **kwargs):
        if event_name in cls._listeners:
            for callback in list(cls._listeners[event_name]):
                try:
                    callback(*args, **kwargs)
                except Exception as e:
                    logging.error(f"Error in listener for {event_name}: {e}")

# Standard Event Names
EVENT_TRANSACTION_UPDATED = "transaction_updated"
EVENT_CATEGORY_UPDATED = "category_updated"
EVENT_NOTIFICATION_RECEIVED = "notification_received"
EVENT_THEME_TOGGLED = "theme_toggled"
