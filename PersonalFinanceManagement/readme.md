# 📝 Quản lý Chi Tiêu Cá Nhân bằng WPF + SQLite + Dapper

## 🎯 Mục tiêu

Phát triển một ứng dụng **Quản lý Chi Tiêu Cá Nhân** sử dụng **WPF** theo mô hình **MVVM**. Dữ liệu được lưu trữ trong **SQLite** và thao tác thông qua **Dapper** để đơn giản hóa việc truy vấn cơ sở dữ liệu.

---

## 🔎 Yêu cầu chi tiết

### 📌 **1. Chức năng chính**

#### ✅ **1.1. Quản lý thu nhập**

- Thêm, sửa, xóa các khoản thu nhập.
- Phân loại thu nhập theo nguồn (lương, thưởng, đầu tư…).
- Tính tổng thu nhập trong tháng, năm.

#### ✅ **1.2. Quản lý chi tiêu**

- Thêm, sửa, xóa các khoản chi tiêu.
- Phân loại chi tiêu theo danh mục (ăn uống, đi lại, giải trí…).
- Tính tổng chi tiêu theo ngày, tháng, năm.

#### ✅ **1.3. Quản lý số dư**

- Tính toán số dư dựa trên tổng thu nhập và tổng chi tiêu.
- Hiển thị cảnh báo khi số dư xuống dưới một ngưỡng nhất định.

#### ✅ **1.4. Xem báo cáo**

- Biểu đồ tròn (Pie Chart) → Thể hiện tỷ lệ chi tiêu theo danh mục.
- Biểu đồ cột (Bar Chart) → Thể hiện thu nhập và chi tiêu theo tháng.
- Lọc báo cáo theo ngày, tháng, năm.

#### ✅ **1.5. Quản lý danh mục thu/chi**

- Thêm, sửa, xóa danh mục (ăn uống, đi lại, đầu tư…).
- Danh mục được lưu trong CSDL.

---

### 🖥️ **2. Yêu cầu UI**

- **MainWindow**:
  - Sidebar → Chọn các mục Thu nhập, Chi tiêu, Báo cáo.
  - Header → Hiển thị số dư hiện tại.
- **Page Thu nhập**:
  - Danh sách thu nhập → `DataGrid`
  - Thêm mới, sửa, xóa → `Dialog`
- **Page Chi tiêu**:
  - Danh sách chi tiêu → `DataGrid`
  - Thêm mới, sửa, xóa → `Dialog`
- **Page Báo cáo**:
  - Biểu đồ cột và biểu đồ tròn → `LiveCharts`

---

### 💾 **3. Yêu cầu kỹ thuật**

✅ **Ngôn ngữ**: C# (.NET 8)\
✅ **UI**: WPF (MVVM)\
✅ **Database**: SQLite\
✅ **ORM**: Dapper\
✅ **Thư viện phụ trợ**:

- Microsoft DependencyINjection → quản lý các Dịch vụ 
- `OxyPlot` → Vẽ biểu đồ
- `Newtonsoft.Json` → Xử lý JSON

---

### 🏗️ **4. Yêu cầu thiết kế**

#### 🔹 **Entity chính**

- `Income` → Bảng quản lý thu nhập
- `Expense` → Bảng quản lý chi tiêu
- `Category` → Bảng danh mục thu/chi
- `Report` → Tính toán báo cáo từ dữ liệu thu/chi

#### 🔹 **Kết nối cơ sở dữ liệu bằng Dapper**

- Tạo interface và class repository cho **Income**, **Expense**, **Category**.
- Viết các hàm cơ bản:
  - `GetAll`, `GetById`, `Insert`, `Update`, `Delete`
  - Dùng `IDbConnection` để thao tác với SQLite qua Dapper.

#### 🔹 **Quản lý trạng thái với ViewModel**

- `IncomeViewModel`, `ExpenseViewModel`, `ReportViewModel`
- Sử dụng `ObservableCollection` để binding dữ liệu với UI.
- Sử dụng `RelayCommand` để thực hiện thao tác thêm, sửa, xóa.

---

### 🔥 **5. Yêu cầu bổ sung**

✅ Tự động tính toán tổng thu/chi khi có thay đổi.\
✅ Cho phép xuất báo cáo ra **Excel** hoặc **PDF**.\
✅ Cho phép tìm kiếm và lọc theo khoảng thời gian.\
✅ Hỗ trợ **Dark Mode** 🌙.

---

### 🚀 **6. Mục tiêu hoàn thành**

| **Giai đoạn** | **Thời gian** | **Mục tiêu**                                       |
| ------------- | ------------- | -------------------------------------------------- |
| **Phase 1**   | 3 giờ         | Tạo cấu trúc dự án, kết nối DB, thiết kế UI cơ bản |
| **Phase 2**   | 4 giờ         | Xây dựng chức năng thu nhập, chi tiêu, danh mục    |
| **Phase 3**   | 2 giờ         | Xây dựng báo cáo và biểu đồ                        |
| **Phase 4**   | 2 giờ         | Hoàn thiện UI, thêm tính năng xuất báo cáo         |

---

### ✅ **Tổng kết**

👉 Dự án này không quá phức tạp nhưng đủ để luyện kỹ năng **MVVM**, **Dapper**, và **SQLite**.\
👉 Nếu làm chuẩn, sau này có thể mở rộng thêm tính năng như **đa người dùng**, **đồng bộ dữ liệu** hoặc **API**! 😎🔥

