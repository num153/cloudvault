# CloudVault Backend Service

Thành phần Backend chịu trách nhiệm xử lý toàn bộ logic nghiệp vụ của CloudVault:
- Xác thực & Phân quyền (JWT, User / Admin).
- Quản lý tệp, thư mục và tạo Presigned URL tương tác với MinIO S3.
- Kiểm tra Quota giới hạn dung lượng trước khi tải lên.
- Ghi nhận nhật ký sử dụng (Metering: dung lượng lưu trữ, băng thông tải xuống).
- Tính cước tự động (Billing) và tích hợp cổng thanh toán Sandbox.

## Gợi ý Tech Stack
- **Ngôn ngữ:** Python 3.11+ / Node.js (TypeScript)
- **Framework:** FastAPI / NestJS
- **Database ORM:** SQLAlchemy + Alembic (Python) hoặc Prisma / TypeORM (TypeScript)
- **S3 Client:** `boto3` (Python) hoặc `@aws-sdk/client-s3` (TypeScript)
- **Background Jobs:** Celery / APScheduler / Cron
