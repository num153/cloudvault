# Kiến trúc hệ thống CloudVault

Tài liệu mô tả kiến trúc tổng thể, các thành phần công nghệ và mô hình triển khai của CloudVault trên nền tảng AWS Academy Learner Lab.

---

## 1. Sơ đồ kiến trúc tổng quan (High-Level Architecture)

```
                       +-----------------------------------+
                       |           Internet / Client       |
                       |       (Web Browser / Mobile)      |
                       +-----------------+-----------------+
                                         |
                                         | HTTP / HTTPS (Port 80/443)
                                         v
                       +-----------------------------------+
                       |        Nginx Reverse Proxy        |
                       +--------+------------------+-------+
                                |                  |
          /api/..., /auth/...   |                  | /* (Static / SSR)
                                v                  v
       +----------------------------+   +----------------------------+
       |       Backend API          |   |      Frontend (Web App)    |
       | (FastAPI / NestJS)         |   |      (React / Next.js)     |
       +--------------+-------------+   +----------------------------+
                      |
                      | Direct S3 Presigned URLs (Upload/Download)
                      |
        +-------------+-------------+
        |                           |
        v                           v
+------------------+      +--------------------+
|  PostgreSQL DB   |      | MinIO Object Store |
| (Metadata, Auth, |      |  (S3-Compatible,   |
|  Billing, Usage) |      |   User Data Files) |
+------------------+      +--------------------+
        ^                           ^
        |                           |
        +-------------+-------------+
                      |
           [EBS gp3 Persistent Volume]
```

---

## 2. Các tầng hệ thống (System Layers)

### 2.1. Tầng giao diện & Điều hướng (Presentation & Gateway)
- **Nginx Reverse Proxy:**
  - Lắng nghe cổng `80` (HTTP) và `443` (HTTPS).
  - Phân luồng yêu cầu:
    - `/` -> Frontend Web App (port `3000`).
    - `/api/` -> Backend REST API (port `8000`).
    - `/minio/` hoặc domain s3 -> MinIO API/Console (port `9000`/`9001`).
  - Hỗ trợ nén Gzip, giới hạn kích thước body (`client_max_body_size 1024M` cho multipart upload), cache static files.
- **Frontend App:**
  - Xây dựng bằng React / Next.js / Vite + Tailwind CSS.
  - Tương tác với backend thông qua JWT Bearer authentication.
  - Sử dụng Presigned URL nhận từ backend để upload/download tệp trực tiếp lên MinIO, tránh quá tải server API.

### 2.2. Tầng ứng dụng & Xử lý nghiệp vụ (Application Layer)
- **Backend Service:**
  - Framework gợi ý: FastAPI (Python) hoặc NestJS / Express (TypeScript).
  - Cung cấp RESTful API: xác thực (JWT), quản lý tệp/thư mục, phân quyền (RBAC: User/Admin), kiểm tra quota, quản lý gói dịch vụ và thanh toán.
  - **S3 Client (boto3 / @aws-sdk/client-s3):** Sinh Presigned URL (PutObject/GetObject), tạo bucket/prefix cho người dùng mới.
  - **Background Worker / Cron Jobs:**
    - Định kỳ (hàng ngày lúc 00:00 UTC) chốt số liệu lưu trữ (`storage_bytes`), tính băng thông tải xuống (`egress_bytes`).
    - Chu kỳ cuối tháng: tự động lập hóa đơn (`invoices`) và gửi thông báo cước.

### 2.3. Tầng lưu trữ & Dữ liệu (Data Layer)
- **PostgreSQL Database:**
  - Lưu trữ dữ liệu quan hệ: thông tin người dùng, bảng phân quyền, metadata tệp/thư mục, liên kết chia sẻ, nhật ký sử dụng, thông tin gói cước và hóa đơn.
- **MinIO Object Storage:**
  - Tương thích chuẩn Amazon S3 API.
  - Lưu trữ toàn bộ dữ liệu nhị phân (binary objects) của người dùng.
  - Dữ liệu được tổ chức theo cấu trúc: `bucket-name / user_id / object_uuid_or_path`.

---

## 3. Kiến trúc triển khai trên AWS Academy Learner Lab

Do đặc thù của môi trường **AWS Learner Lab** (giới hạn 100 USD, session 4 tiếng tự tắt máy, quyền hạn chế với IAM):

1. **Kiến trúc Single-Node EC2:**
   - Sử dụng 1 EC2 instance loại `t3.medium` (hoặc `t3.small`) chạy Ubuntu 22.04 LTS.
   - Toàn bộ dịch vụ (Nginx, Frontend, Backend, PostgreSQL, MinIO) được đóng gói và khởi chạy thông qua **Docker Compose**.
2. **Lưu trữ bền vững (Persistent Storage):**
   - Dữ liệu PostgreSQL và MinIO được mount ra volume EBS gp3 gắn vào EC2 hoặc Docker named volumes.
   - Script tự động backup database và metadata lên S3 bucket bên ngoài (nếu lab cho phép) hoặc lưu dump định kỳ.
3. **Phục hồi nhanh sau khi Lab Reset (Disaster Recovery):**
   - Sử dụng script **EC2 User-Data** (`infra/scripts/ec2-user-data.sh`).
   - Khi khởi động instance mới, script tự động:
     1. Cài đặt Docker & Docker Compose.
     2. Clone source code dự án từ Git repository.
     3. Copy file `.env` cấu hình.
     4. Chạy `docker compose up -d --build`.
   - Toàn bộ hệ thống sẵn sàng hoạt động trong vòng dưới 10 phút.
