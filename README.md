# Ứng Dụng Quản Lý Tài Chính Cá Nhân

Ứng dụng desktop hiện đại giúp quản lý tài chính cá nhân được xây dựng bằng WPF, SQLite và Dapper, theo mô hình thiết kế MVVM.

## Tổng Quan

Ứng dụng này giúp người dùng quản lý tài chính cá nhân bằng cách theo dõi thu nhập, chi tiêu và cung cấp báo cáo tài chính chi tiết kèm biểu đồ trực quan. Giao diện hiện đại, hỗ trợ chế độ tối và các công cụ quản lý tài chính toàn diện.

## Công Nghệ Sử Dụng

-   **Nền tảng**: C# (.NET 8)
-   **Giao diện**: WPF (Windows Presentation Foundation)
-   **Kiến trúc**: MVVM (Model-View-ViewModel)
-   **Cơ sở dữ liệu**: SQLite
-   **ORM**: Dapper
-   **Thư viện bổ sung**:
    -   Microsoft.Extensions.DependencyInjection - Quản lý các dependency
    -   OxyPlot - Vẽ biểu đồ
    -   Newtonsoft.Json - Xử lý JSON
    -   ClosedXML - Xuất file Excel

## Tính Năng

### 1. Quản Lý Thu Nhập

-   Thêm, sửa, xóa các khoản thu nhập
-   Phân loại nguồn thu (lương, đầu tư, thưởng, v.v.)
-   Tính tổng thu nhập theo tháng và năm

### 2. Quản Lý Chi Tiêu

-   Thêm, sửa, xóa các khoản chi tiêu
-   Phân loại chi tiêu (ăn uống, đi lại, giải trí, v.v.)
-   Theo dõi chi tiêu theo ngày, tháng và năm

### 3. Quản Lý Số Dư

-   Tự động tính toán số dư dựa trên thu nhập và chi tiêu
-   Cảnh báo khi số dư thấp
-   Cập nhật số dư theo thời gian thực

### 4. Báo Cáo và Phân Tích

-   Biểu đồ tròn thể hiện tỷ lệ chi tiêu theo danh mục
-   Biểu đồ cột so sánh thu nhập và chi tiêu theo tháng
-   Lọc báo cáo theo khoảng thời gian
-   Xuất báo cáo ra Excel

### 5. Quản Lý Danh Mục

-   Tạo, sửa và xóa danh mục tùy chỉnh
-   Phân biệt danh mục thu nhập và chi tiêu
-   Lưu trữ danh mục trong cơ sở dữ liệu

### 6. Tính Năng Bổ Sung

-   Hỗ trợ giao diện sáng/tối
-   Lọc theo khoảng thời gian
-   Tìm kiếm
-   Xuất báo cáo Excel
-   Tính toán tự động
-   Giao diện người dùng hiện đại và linh hoạt

## Cài Đặt

1. Đảm bảo đã cài đặt .NET 8 SDK
2. Clone repository về máy
3. Di chuyển vào thư mục dự án
4. Chạy các lệnh sau:

```bash
dotnet restore
dotnet build
dotnet run
```

## Cấu Trúc Dự Án

-   `Models/` - Các model dữ liệu
-   `ViewModels/` - ViewModel và các command MVVM
-   `Views/` - Giao diện WPF
-   `Data/` - Context và repository database
-   `Services/` - Các service của ứng dụng
-   `Themes/` - Giao diện và style
-   `Converters/` - Chuyển đổi giá trị WPF

## Kiến Trúc

Ứng dụng tuân theo mô hình MVVM:

-   **Models**: Định nghĩa cấu trúc dữ liệu (Transaction, Category, v.v.)
-   **ViewModels**: Xử lý logic nghiệp vụ và quản lý trạng thái
-   **Views**: Định nghĩa giao diện bằng XAML
-   **Repositories**: Xử lý truy cập dữ liệu qua Dapper
-   **Services**: Cung cấp các chức năng xuyên suốt ứng dụng

## Thiết Kế Cơ Sở Dữ Liệu

Các entity chính:

-   `Income`: Quản lý giao dịch thu nhập
-   `Expense`: Quản lý giao dịch chi tiêu
-   `Category`: Quản lý danh mục giao dịch
-   `Report`: Tạo báo cáo tài chính

## Phát Triển Tương Lai

-   Hỗ trợ nhiều người dùng
-   Đồng bộ hóa đám mây
-   Ứng dụng di động đi kèm
-   Tính năng lập kế hoạch ngân sách
-   Tích hợp API
-   Sao lưu/khôi phục dữ liệu

## Bản Quyền

Đã đăng ký bản quyền. Chỉ sử dụng cho mục đích cá nhân.
