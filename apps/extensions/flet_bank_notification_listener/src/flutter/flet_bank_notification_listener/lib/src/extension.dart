import 'package:flet/flet.dart';
import 'package:flutter/widgets.dart';

import 'flet_bank_notification_listener.dart';

class Extension extends FletExtension {
  @override
  Widget? createWidget(Key? key, Control control) {
    switch (control.type) {
      case "FletBankNotificationListener":
        return FletBankNotificationListenerControl(control: control);
      default:
        return null;
    }
  }
}
