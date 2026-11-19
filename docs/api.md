# Tài liệu Đặc tả REST API - CloudVault

Tài liệu chi tiết về các điểm cuối (Endpoints), định dạng dữ liệu (Payload) và mã trạng thái trả về của hệ thống CloudVault.

- **Base URL cục bộ:** `http://localhost:8000/api/v1`
- **Xác thực:** Bearer Token (JWT) gửi qua header `Authorization: Bearer <access_token>`.

---

## 1. Authentication & Users (`/auth`)

### 1.1. Đăng ký tài khoản
- **Endpoint:** `POST /auth/register`
- **Request Body:**
```json
{
  "email": "user@example.com",
  "password": "StrongPassword123!",
  "full_name": "Nguyen Van A"
}
```
- **Response 201 Created:**
```json
{
  "message": "Đăng ký thành công",
  "user": {
    "id": "usr_1029384",
    "email": "user@example.com",
    "full_name": "Nguyen Van A",
    "role": "user",
    "plan": "Free"
  }
}
```

### 1.2. Đăng nhập
- **Endpoint:** `POST /auth/login`
- **Request Body:**
```json
{
  "email": "user@example.com",
  "password": "StrongPassword123!"
}
```
- **Response 200 OK:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsIn...",
  "token_type": "bearer",
  "expires_in": 86400,
  "user": {
    "id": "usr_1029384",
    "email": "user@example.com",
    "full_name": "Nguyen Van A",
    "role": "user"
  }
}
```

### 1.3. Lấy thông tin tài khoản hiện tại
- **Endpoint:** `GET /auth/me`
- **Headers:** `Authorization: Bearer <token>`
- **Response 200 OK:**
```json
{
  "id": "usr_1029384",
  "email": "user@example.com",
  "full_name": "Nguyen Van A",
  "role": "user",
  "quota_limit_bytes": 1073741824,
  "quota_used_bytes": 245600000
}
```

---

## 2. Quản lý Tệp và Thư mục (`/files`, `/folders`)

### 2.1. Lấy danh sách tệp & thư mục
- **Endpoint:** `GET /files`
- **Query Params:**
  - `parent_id` (optional): ID thư mục cha (mặc định null = root)
  - `page` (int, default 1)
  - `limit` (int, default 50)
  - `sort_by` (name | size | created_at)
  - `order` (asc | desc)
  - `search` (optional string): tìm kiếm theo tên tệp
- **Response 200 OK:**
```json
{
  "items": [
    {
      "id": "fil_884920",
      "name": "BaoCaoCuoiKy.pdf",
      "is_folder": false,
      "size": 1548290,
      "content_type": "application/pdf",
      "created_at": "2026-11-19T20:00:00Z"
    },
    {
      "id": "fld_110293",
      "name": "TaiLieuHocTap",
      "is_folder": true,
      "size": 0,
      "created_at": "2026-11-18T10:00:00Z"
    }
  ],
  "total": 2,
  "page": 1,
  "limit": 50
}
```

### 2.2. Yêu cầu Presigned URL để Upload
- **Endpoint:** `POST /files/upload-url`
- **Request Body:**
```json
{
  "name": "photo_backup.zip",
  "size": 52428800,
  "content_type": "application/zip",
  "parent_id": null
}
```
- **Xử lý:** Backend kiểm tra dung lượng còn lại so với Quota. Nếu vượt mức -> trả về `403 Forbidden` kèm thông báo.
- **Response 200 OK:**
```json
{
  "upload_url": "http://s3.cloudvault.local/cloudvault-bucket/usr_1029384/uuid_photo.zip?X-Amz-Signature=...",
  "file_id": "fil_993821",
  "expires_in": 900
}
```

### 2.3. Xác nhận Upload hoàn tất
- **Endpoint:** `POST /files/{id}/complete-upload`
- **Response 200 OK:**
```json
{
  "message": "Tệp đã được ghi nhận thành công",
  "file_id": "fil_993821",
  "size": 52428800
}
```

### 2.4. Yêu cầu Presigned URL để Download
- **Endpoint:** `GET /files/{id}/download-url`
- **Response 200 OK:**
```json
{
  "download_url": "http://s3.cloudvault.local/cloudvault-bucket/usr_1029384/uuid_photo.zip?X-Amz-Signature=...",
  "expires_in": 300
}
```

### 2.5. Tạo thư mục mới
- **Endpoint:** `POST /folders`
- **Request Body:**
```json
{
  "name": "DoAnTotNghiep",
  "parent_id": null
}
```

### 2.6. Xóa tệp hoặc thư mục
- **Endpoint:** `DELETE /files/{id}`
- **Response 200 OK:**
```json
{
  "message": "Xóa thành công"
}
```

---

## 3. Chia sẻ tệp (`/shares`)

### 3.1. Tạo link chia sẻ
- **Endpoint:** `POST /shares`
- **Request Body:**
```json
{
  "file_id": "fil_884920",
  "expires_in_hours": 24,
  "password": null
}
```
- **Response 201 Created:**
```json
{
  "share_url": "http://cloudvault.local/s/sh_928fka819a",
  "token": "sh_928fka819a",
  "expires_at": "2026-11-20T20:00:00Z"
}
```

### 3.2. Truy cập tệp từ link chia sẻ công khai
- **Endpoint:** `GET /s/{token}`
- **Headers:** Không yêu cầu đăng nhập.
- **Response 200 OK:**
```json
{
  "file_name": "BaoCaoCuoiKy.pdf",
  "file_size": 1548290,
  "download_url": "http://s3.cloudvault.local/...",
  "has_password": false
}
```

---

## 4. Gói cước & Đo lường (`/plans`, `/usage`)

### 4.1. Danh sách các gói cước
- **Endpoint:** `GET /plans`
- **Response 200 OK:**
```json
[
  {
    "id": "plan_free",
    "name": "Free",
    "quota_gb": 1,
    "price_month": 0,
    "price_per_extra_gb": 0,
    "price_per_egress_gb": 0
  },
  {
    "id": "plan_basic",
    "name": "Basic",
    "quota_gb": 20,
    "price_month": 50000,
    "price_per_extra_gb": 2000,
    "price_per_egress_gb": 1000
  },
  {
    "id": "plan_pro",
    "name": "Pro",
    "quota_gb": 100,
    "price_month": 200000,
    "price_per_extra_gb": 2000,
    "price_per_egress_gb": 1000
  }
]
```

### 4.2. Xem mức sử dụng hiện tại
- **Endpoint:** `GET /usage`
- **Response 200 OK:**
```json
{
  "storage_bytes_used": 154829000,
  "storage_quota_bytes": 1073741824,
  "egress_bytes_this_month": 45000000,
  "requests_count_this_month": 128
}
```

---

## 5. Hóa đơn & Thanh toán Sandbox (`/invoices`, `/payments`)

### 5.1. Danh sách hóa đơn của người dùng
- **Endpoint:** `GET /invoices`
- **Response 200 OK:**
```json
[
  {
    "id": "inv_202611_01",
    "period": "2026-11",
    "amount": 50000,
    "status": "UNPAID",
    "due_date": "2026-12-05T00:00:00Z"
  }
]
```

### 5.2. Khởi tạo thanh toán hóa đơn
- **Endpoint:** `POST /invoices/{id}/pay`
- **Request Body:**
```json
{
  "provider": "vnpay_sandbox"
}
```
- **Response 200 OK:** Trả về đường dẫn chuyển hướng sang cổng thanh toán sandbox:
```json
{
  "payment_url": "https://sandbox.vnpayment.vn/paymentv2/vpcpay.html?..."
}
```

### 5.3. Callback / Webhook nhận kết quả thanh toán
- **Endpoint:** `POST /payments/callback`
- **Xử lý:** Xác thực checksum từ cổng thanh toán, cập nhật trạng thái hóa đơn sang `PAID`.

---

## 6. API Quản trị viên (`/admin`)

- Yêu cầu token có vai trò `role: "admin"`.
- `GET /admin/users`: Danh sách tất cả người dùng, trạng thái và dung lượng đã dùng.
- `PATCH /admin/users/{id}`: Khóa / mở khóa tài khoản người dùng (`status: "active" | "suspended"`).
- `CRUD /admin/plans`: Tạo, cập nhật hoặc vô hiệu hóa các gói dịch vụ.
- `GET /admin/stats`: Báo cáo tổng thể: số người dùng đăng ký, tổng dung lượng tệp lưu trữ, tổng doanh thu dự kiến trong tháng.
