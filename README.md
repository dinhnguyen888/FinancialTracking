# CashflowTracking

> **Ứng dụng theo dõi tài chính cá nhân thông minh, bảo mật và tự động hóa dòng tiền trên nền tảng Android.**

---

## Tổng Quan Dự Án (Project Overview)

**CashflowTracking** là ứng dụng quản lý chi tiêu và theo dõi dòng tiền cá nhân được xây dựng với triết lý **Offline-First (ưu tiên ngoại tuyến)** và **Bảo mật tuyệt đối (100% On-Device)**. 

Khác với các ứng dụng thông thường yêu cầu người dùng phải gõ tay từng giao dịch hàng ngày, CashflowTracking giải quyết triệt để vấn đề này bằng tính năng **Tự động bắt biến động số dư ngầm** từ thông báo ngân hàng, ví điện tử và email giao dịch, giúp việc ghi chép chi tiêu diễn ra tức thì mà không tốn công sức.

### Tính Năng Nổi Bật

1. **Tự động bắt giao dịch ngân hàng & Email (Tính năng cốt lõi):**
   - Lắng nghe biến động số dư nền từ các ngân hàng và ví điện tử phổ biến tại Việt Nam: **Sacombank, Vietcombank, MB Bank, Techcombank, TPBank, VPBank, ACB, BIDV, Cake by VPBank, MoMo, ZaloPay...**
   - Bắt và bóc tách thông báo giao dịch gửi về qua **Gmail / Email app**.
   - Bộ bóc tách thông minh (**Vietnamese Bank Notification Parser**) tự động nhận diện: Ngân hàng, Số tiền, Loại giao dịch (Thu / Chi), Nội dung và gợi ý Danh mục phù hợp.
2. **Hệ thống chống trùng lặp đa lớp (Smart Multi-layered Deduplication):**
   - Tự động bỏ qua thông báo gom nhóm của Gmail (`FLAG_GROUP_SUMMARY`).
   - Băm nội dung (MD5 Fingerprint) kèm cơ chế Cooldown 10 phút, ngăn chặn Gmail gửi trùng thông báo khi đồng bộ nền.
   - Kiểm tra trùng lặp trong cơ sở dữ liệu SQLite trước khi lưu và tự động dọn dẹp các bản ghi rác.
3. **Hộp thư chờ duyệt (Pending Inbox):**
   - Các giao dịch mới xuất hiện trong Hộp thư để người dùng xác nhận nhanh hoặc điều chỉnh danh mục chỉ với một chạm.
   - Hỗ trợ nút **"Dán Email/SMS"** để phân tích nhanh giao dịch khi người dùng copy nội dung thủ công.
4. **Quản lý tài chính toàn diện:**
   - **Dashboard trực quan:** Thống kê thu nhập, chi tiêu, tổng số dư trong tháng.
   - **Hạn mức ngân sách:** Cài đặt định mức chi tiêu tháng và theo dõi tỷ lệ đã tiêu dùng.
   - **Báo cáo & Danh mục:** Phân bổ chi tiêu theo biểu đồ và danh mục tùy biến linh hoạt.
5. **Bảo mật & Quyền riêng tư:**
   - Hoàn toàn không gửi dữ liệu giao dịch hay tin nhắn lên bất kỳ máy chủ cloud nào.
   - Dữ liệu lưu trữ độc lập trong SQLite (`cashflow.db`) trực tiếp trên bộ nhớ thiết bị.

---

## Phiên Bản Android Hỗ Trợ (Android Compatibility)

| Thông số | Giá trị | Ghi chú |
| :--- | :--- | :--- |
| **Phiên bản tối thiểu (Min SDK)** | **Android 7.0 (API Level 24)** | Tương thích hầu hết các thiết bị Android phổ biến hiện nay |
| **Phiên bản mục tiêu (Target SDK)** | **Android 15 / 16 (API Level 36)** | Tối ưu hóa hiệu năng, bảo mật và tương thích các bản Android mới nhất |
| **Giao diện tùy biến hỗ trợ** | Xiaomi HyperOS/MIUI, Samsung One UI, Oppo ColorOS, Vivo OriginOS, Google Pixel UI... | Cần bật quyền "Truy cập thông báo" (Notification Access) trong Cài đặt hệ thống |

---

## Kiến Trúc Công Nghệ (Tech Stack)

* **UI Framework:** [Flet](https://flet.dev/) (Nền tảng Flutter engine mang lại giao diện mượt mà 60/120fps, Dark theme hiện đại).
* **Core Runtime:** Python 3.11 nhúng qua [Serious Python](https://github.com/flet-dev/serious-python).
* **Native Android Layer:** Kotlin Service (`BankNotificationListener.kt`) kế thừa `NotificationListenerService` của Android Framework.
* **Database:** SQLite3 (Cục bộ, không phụ thuộc mạng).
* **Kiến trúc luồng sự kiện:** Reactive EventBus hỗ trợ cập nhật dữ liệu thời gian thực giữa background worker và giao diện người dùng.

---

## Cấu Trúc Thư Mục Dự Án (Project Structure)

```text
FinancialTracking/
├── apps/
│   ├── core/                  # Cấu hình hệ thống, Theme, EventBus
│   ├── database/              # SQLite Database, Connection pool, Repositories
│   ├── models/                # Data models (Transaction, Category, Notification)
│   ├── services/              # Notification Listener Service, Regex Parser
│   ├── ui/                    # Giao diện Flet
│   │   ├── components/        # Các component dùng chung (Cards, Modals, Banners)
│   │   └── views/             # Các màn hình chính (Dashboard, Transactions, Inbox, Reports)
│   ├── template/              # Template mã nguồn Native Android (Kotlin, Manifest, Drawables)
│   ├── scripts/               # Bộ script tự động build và cài đặt
│   │   ├── build.sh           # Script đóng gói APK hoàn chỉnh
│   │   └── install.sh         # Script cài đặt APK trực tiếp qua ADB
│   └── main.py                # Điểm khởi chạy chính của ứng dụng
├── README.md                  # Tài liệu tổng quan dự án
└── pyproject.toml             # Quản lý dependencies
```

---

## Hướng Dẫn Cài Đặt & Đóng Gói (Build & Installation)

### 1. Cài đặt trực tiếp file APK
File APK sau khi build nằm tại:
```bash
apps/build/apk/CashflowTracking.apk
```
Bạn có thể copy file này vào điện thoại để cài đặt hoặc sử dụng lệnh cài tự động qua ADB:
```bash
bash apps/scripts/install.sh
```

### 2. Tự đóng gói (Build from Source)
Yêu cầu môi trường đã cài đặt:
- Flutter SDK (hỗ trợ Android)
- Android SDK (API Level 34+)
- Python 3.10+ cùng môi trường ảo `.venv` trong thư mục `apps/`

Thực hiện lệnh:
```bash
bash apps/scripts/build.sh
```
Script sẽ tự động:
1. Đồng bộ code native Kotlin (`BankNotificationListener.kt`, icon, styles) vào dự án Flutter.
2. Đóng gói mã nguồn Python và assets.
3. Chạy Gradle để xuất ra file APK Release hoàn chỉnh tại `apps/build/apk/CashflowTracking.apk`.

---

## Thiết Lập Sau Khi Cài Đặt Lần Đầu

Để ứng dụng có thể bắt thông báo tự động, bạn cần cấp quyền lắng nghe thông báo trên điện thoại:
1. Mở ứng dụng **CashflowTracking**.
2. Trên banner thông báo quyền, bấm **"Cấp quyền ngay"** (hoặc vào **Cài đặt máy** $\rightarrow$ **Ứng dụng** $\rightarrow$ **Quyền truy cập đặc biệt** $\rightarrow$ **Quyền truy cập thông báo**).
3. Bật cho phép **CashflowTracking**.
4. *(Tùy chọn đối với Xiaomi/Oppo/Vivo)*: Bật quyền **Tự khởi chạy (Autostart)** và chuyển cấu hình tiết kiệm pin sang **Không hạn chế (No restrictions)** để ứng dụng không bị hệ thống tắt khi chạy nền.
