# CloudVault Frontend Web Client

Ứng dụng Web Client cho người dùng và quản trị viên của hệ thống CloudVault.

## Các chức năng giao diện chính
1. **Public:** Trang chủ giới thiệu, Bảng giá gói cước, Đăng ký & Đăng nhập.
2. **User Dashboard:**
   - Trình duyệt tệp (File Explorer): upload drag-drop, download, tạo thư mục, xóa/đổi tên.
   - Hiển thị thanh tiến độ dung lượng lưu trữ (Quota progress bar).
   - Quản lý liên kết chia sẻ tệp.
   - Thống kê mức sử dụng theo ngày/tháng (biểu đồ usage).
   - Hóa đơn cước phí và nút thanh toán qua cổng sandbox.
3. **Admin Dashboard:**
   - Quản lý danh sách người dùng (khóa/mở khóa tài khoản).
   - Cấu hình gói cước và bảng giá.
   - Xem thống kê tổng quan toàn hệ thống.

## Gợi ý Tech Stack
- **Framework:** React / Next.js / Vite
- **CSS:** Tailwind CSS, shadcn/ui hoặc Ant Design
- **State & HTTP:** Axios / TanStack Query, Zustand / Redux
- **Upload:** Tải lên trực tiếp qua S3 Presigned URL kèm thanh tiến trình (progress bar).
