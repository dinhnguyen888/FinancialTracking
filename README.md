# Hướng dẫn Tích hợp Android Notification Listener cho CashflowTracking Flet Mobile

Tài liệu này hướng dẫn cách cấu hình và đóng gói ứng dụng **CashflowTracking Flet Mobile** thành file APK Android hoàn chỉnh, có khả năng tự động bắt thông báo biến động số dư từ các ứng dụng ngân hàng tại Việt Nam (Sacombank Pay, Cake Bank, MoMo, Vietcombank, MB Bank, Techcombank, TPBank...).

---

## 1. Cơ Chế Hoạt Động Trên Android

1. **Quyền hệ thống**: Android yêu cầu quyền `android.permission.BIND_NOTIFICATION_LISTENER_SERVICE` để đọc thanh thông báo của hệ thống.
2. **Cấp quyền từ người dùng**: Khi cài đặt app lần đầu, người dùng vào **Cài đặt điện thoại** $\rightarrow$ **Ứng dụng** $\rightarrow$ **Quyền truy cập đặc biệt** $\rightarrow$ **Quyền truy cập thông báo (Notification Access)** $\rightarrow$ Bật cho phép **CashflowTracking**.
3. **Bóc tách thông báo**: `NotificationListenerService` nhận chuỗi thông báo $\rightarrow$ chuyển đến `BankNotificationParser` $\rightarrow$ tự động nhận diện Số tiền, Thu (+)/Chi (-), Ngân hàng, Nội dung $\rightarrow$ Lưu vào bảng `bank_notifications` để người dùng xác nhận hoặc tự động ghi sổ.

---

## 2. Cấu hình Android Manifest (`AndroidManifest.xml`)

Thêm Service vào bên trong thẻ `<application>`:

```xml
<service
    android:name=".BankNotificationService"
    android:label="CashflowTracking Notification Listener"
    android:permission="android.permission.BIND_NOTIFICATION_LISTENER_SERVICE"
    android:exported="true">
    <intent-filter>
        <action android:name="android.service.notification.NotificationListenerService" />
    </intent-filter>
</service>
```

---

## 3. Mã Nguồn Kotlin Lắng Nghe Thông Báo (`BankNotificationService.kt`)

```kotlin
package com.cashflowtracking.app

import android.service.notification.NotificationListenerService
import android.service.notification.StatusBarNotification
import android.util.Log

class BankNotificationService : NotificationListenerService() {
    override fun onNotificationPosted(sbn: StatusBarNotification?) {
        super.onNotificationPosted(sbn)
        if (sbn == null) return

        val packageName = sbn.packageName ?: return
        val extras = sbn.notification.extras ?: return
        val title = extras.getString("android.title") ?: ""
        val text = extras.getCharSequence("android.text")?.toString() ?: ""

        // Danh sách package các app ngân hàng & ví điện tử phổ biến
        val bankPackages = listOf(
            "com.vnpay.sacombank",        // Sacombank Pay
            "com.cake.bank",              // Cake by VPBank
            "com.mservice.momopay",       // MoMo
            "com.mservice.momotransfer",  // MoMo
            "com.VCB",                    // Vietcombank
            "com.mbmobile",               // MB Bank
            "vn.com.techcombank.bb.app",  // Techcombank
            "com.tpb.mb.gprsandroid",     // TPBank
            "com.vnpay.bidv",             // BIDV
            "vn.com.vng.zalopay"          // ZaloPay
        )

        if (bankPackages.any { packageName.contains(it, ignoreCase = true) }) {
            Log.d("CashflowTracking", "Bắt được thông báo ngân hàng từ $packageName: $title - $text")
            // Gửi message qua Event / BroadcastReceiver / Ghi trực tiếp vào SQLite finance.db
        }
    }

    override fun onNotificationRemoved(sbn: StatusBarNotification?) {
        super.onNotificationRemoved(sbn)
    }
}
```

---

## 4. Lệnh Đóng Gói APK với Flet

Cài đặt Flet CLI và Flutter SDK (máy bạn đã có sẵn Flutter 3.44):

```bash
# Di chuyển vào thư mục apps
cd apps

# Build file APK Release cho Android
flet build apk --project "CashflowTracking" --org "com.cashflowtracking"
```
File APK xuất ra sẽ nằm tại thư mục `build/apk/`.
