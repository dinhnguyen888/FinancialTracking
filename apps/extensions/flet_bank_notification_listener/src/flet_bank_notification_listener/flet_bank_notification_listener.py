from enum import Enum
from typing import Any, Optional, Callable, List
import flet as ft

@ft.control("FletBankNotificationListener")
class FletBankNotificationListener(ft.Control):
    """
    FletBankNotificationListener: Flet 1.0 extension control for listening to
    Android notification events from Vietnamese bank apps (Sacombank, Cake Bank, MoMo, etc.)
    """

    value: Optional[str] = None
    package_filters: Optional[List[str]] = None
    on_notification: Optional[Callable[[ft.ControlEvent], None]] = None

    def __init__(
        self,
        value: Optional[str] = None,
        package_filters: Optional[List[str]] = None,
        on_notification: Optional[Callable[[ft.ControlEvent], None]] = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.value = value
        self.package_filters = package_filters or [
            "com.vnpay.sacombank",
            "com.cake.bank",
            "com.mservice.momopay",
            "com.VCB",
            "com.mbmobile",
            "vn.com.techcombank.bb.app",
            "com.tpb.mb.gprsandroid"
        ]
        self.on_notification = on_notification
