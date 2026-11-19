# Đặc tả yêu cầu phần mềm (SRS)

**Dự án:** CloudVault - Hệ thống Cloud Data Storage  
**Môn học:** Điện toán đám mây  
**Phiên bản:** 1.0 (bản nháp)  
**Nhóm thực hiện:** 3 thành viên (điền tên, MSSV)

*Lưu ý: "CloudVault" là tên tạm, có thể thay bằng tên khác của nhóm.*

## 1. Giới thiệu

### 1.1 Mục đích

Tài liệu mô tả yêu cầu cho hệ thống CloudVault: một dịch vụ lưu trữ dữ liệu đám mây (Cloud Data Storage) cho phép người dùng tự đăng ký, lưu trữ và chia sẻ tệp, đồng thời được đo lường mức sử dụng (metering) và tính phí (billing) theo gói dịch vụ. Tài liệu là cơ sở để nhóm thiết kế, cài đặt, kiểm thử và nghiệm thu.

### 1.2 Phạm vi

CloudVault gồm bốn khối chính:

- **Storage engine:** phần mềm lưu trữ đối tượng tương thích S3 (MinIO hoặc Garage) do nhóm tự triển khai trên AWS.
- **Backend:** API do nhóm tự phát triển, xử lý đăng ký, xác thực, quản lý tệp, quota, metering, billing.
- **Frontend:** ứng dụng web cho người dùng và quản trị viên.
- **Billing:** tính cước theo gói và theo mức sử dụng, thanh toán qua cổng sandbox.

Ngoài phạm vi (phiên bản này): đồng bộ desktop/mobile, chỉnh sửa tài liệu trực tuyến, mã hóa phía client, thanh toán bằng tiền thật, SLA thương mại.

### 1.3 Định nghĩa và từ viết tắt

- **SRS:** Software Requirements Specification.
- **Bucket / Object:** đơn vị chứa và đối tượng dữ liệu trong lưu trữ kiểu S3.
- **Presigned URL:** đường dẫn có chữ ký, hết hạn sau thời gian ngắn, dùng để tải lên/xuống trực tiếp với storage.
- **Quota:** hạn mức dung lượng tối đa của người dùng theo gói.
- **Metering:** đo lường mức sử dụng (dung lượng, băng thông, số request).
- **Egress:** lưu lượng dữ liệu tải xuống.
- **Tenant:** một người dùng/tổ chức có không gian lưu trữ cô lập.

### 1.4 Tài liệu tham khảo

- Đề bài môn Điện toán đám mây, đề tài 15: Xây dựng hệ thống Cloud Data Storage.
- Tài liệu MinIO / Garage, Amazon S3 API.
- IEEE 830 / ISO 29148 (cấu trúc SRS).

## 2. Mô tả tổng quan

### 2.1 Góc nhìn sản phẩm

CloudVault hoạt động như một dịch vụ lưu trữ đám mây thu nhỏ, tương tự Google Drive/Dropbox ở lớp người dùng, và S3 ở lớp hạ tầng. Hệ thống triển khai hoàn toàn trên AWS (tài khoản AWS Academy Learner Lab), đóng gói bằng Docker Compose.

### 2.2 Nhóm người dùng

| Vai trò | Mô tả | Quyền chính |
| --- | --- | --- |
| Khách (Guest) | Chưa đăng nhập | Xem trang giới thiệu, bảng giá, đăng ký, đăng nhập |
| Người dùng (User) | Khách hàng đã đăng ký | Quản lý tệp, chia sẻ, đổi gói, xem usage, thanh toán hóa đơn |
| Quản trị viên (Admin) | Vận hành hệ thống | Quản lý người dùng, gói dịch vụ, xem thống kê, khóa/mở tài khoản |

### 2.3 Môi trường và ràng buộc

- Hạ tầng là AWS Academy Learner Lab: ngân sách khoảng 100 USD, session có giới hạn thời gian, tài nguyên có thể bị dừng khi hết session, không tạo được IAM user/role mới (dùng LabRole), chỉ một số region và dịch vụ được phép.
- Không dùng NAT Gateway, hạn chế Elastic IP và dịch vụ tính phí cao để tiết kiệm ngân sách.
- Hệ thống phải dựng lại được nhanh (Infrastructure as Code hoặc script) sau khi lab reset.
- Thanh toán chỉ dùng môi trường sandbox/test.
- Thời gian thực hiện: 3 tuần, nhóm 3 người.

### 2.4 Giả định và phụ thuộc

- Nhóm có quyền tạo EC2, EBS, VPC, Security Group, S3 (nếu cần) trong Learner Lab.
- Có thể truy cập internet từ EC2 để kéo Docker image.
- Email xác nhận gửi qua SMTP bên ngoài (Gmail app password hoặc Mailtrap) vì có thể không dùng được SES.

## 3. Yêu cầu chức năng

Ưu tiên: **M** (Must - bắt buộc), **S** (Should - nên có), **C** (Could - nếu còn thời gian).

### 3.1 Đăng ký và xác thực

| Mã | Yêu cầu | Ưu tiên |
| --- | --- | --- |
| FR-01 | Khách đăng ký tài khoản bằng email, mật khẩu, họ tên; email không được trùng. | M |
| FR-02 | Mật khẩu được băm (bcrypt/argon2), không lưu dạng thô. | M |
| FR-03 | Khi đăng ký, hệ thống tự tạo không gian lưu trữ riêng (bucket hoặc prefix) và gán gói Free. | M |
| FR-04 | Đăng nhập, trả về JWT (access token) và hỗ trợ đăng xuất. | M |
| FR-05 | Xác nhận email qua liên kết gửi về hộp thư. | S |
| FR-06 | Quên mật khẩu / đặt lại mật khẩu. | C |
| FR-07 | Xem và cập nhật hồ sơ cá nhân, đổi mật khẩu. | S |

### 3.2 Quản lý tệp và thư mục

| Mã | Yêu cầu | Ưu tiên |
| --- | --- | --- |
| FR-08 | Tải tệp lên (upload) thông qua presigned URL hoặc qua backend; hiển thị tiến trình. | M |
| FR-09 | Tải tệp xuống (download). | M |
| FR-10 | Xem danh sách tệp/thư mục, có phân trang, sắp xếp theo tên/ngày/dung lượng. | M |
| FR-11 | Tạo thư mục, đổi tên, di chuyển, xóa tệp/thư mục. | M |
| FR-12 | Tìm kiếm tệp theo tên. | S |
| FR-13 | Thùng rác: xóa mềm, khôi phục trong 7-30 ngày. | C |
| FR-14 | Xem trước (preview) ảnh và PDF. | C |
| FR-15 | Mỗi người dùng chỉ truy cập được dữ liệu của chính mình (cô lập tenant). | M |

### 3.3 Chia sẻ

| Mã | Yêu cầu | Ưu tiên |
| --- | --- | --- |
| FR-16 | Tạo liên kết chia sẻ tệp công khai có thời hạn hết hạn. | S |
| FR-17 | Thu hồi liên kết chia sẻ. | S |
| FR-18 | Đặt mật khẩu cho liên kết chia sẻ. | C |

### 3.4 Gói dịch vụ và quota

| Mã | Yêu cầu | Ưu tiên |
| --- | --- | --- |
| FR-19 | Hệ thống có nhiều gói dịch vụ (ví dụ Free, Basic, Pro) với dung lượng và đơn giá khác nhau. | M |
| FR-20 | Chặn upload khi vượt quota của gói và hiển thị thông báo rõ ràng. | M |
| FR-21 | Người dùng xem dung lượng đã dùng / hạn mức dạng thanh tiến độ. | M |
| FR-22 | Người dùng nâng cấp hoặc hạ cấp gói; hiệu lực theo chu kỳ tính phí kế tiếp hoặc ngay lập tức (nhóm chọn một và ghi rõ). | M |
| FR-23 | Cảnh báo khi dùng trên 80% quota. | C |

### 3.5 Đo lường mức sử dụng (Metering)

| Mã | Yêu cầu | Ưu tiên |
| --- | --- | --- |
| FR-24 | Ghi nhận dung lượng lưu trữ của từng người dùng, cập nhật khi upload/xóa. | M |
| FR-25 | Ghi nhận lưu lượng tải xuống (egress) và số request của từng người dùng. | S |
| FR-26 | Job định kỳ (ví dụ hằng ngày) chốt số liệu usage vào bảng thống kê theo ngày/tháng. | M |
| FR-27 | Người dùng xem biểu đồ usage theo thời gian. | S |

### 3.6 Billing và thanh toán

| Mã | Yêu cầu | Ưu tiên |
| --- | --- | --- |
| FR-28 | Cuối mỗi chu kỳ (tháng), hệ thống tự sinh hóa đơn gồm: phí gói + phí vượt mức (dung lượng, egress) theo bảng giá. | M |
| FR-29 | Người dùng xem danh sách hóa đơn và chi tiết từng khoản. | M |
| FR-30 | Thanh toán hóa đơn qua cổng sandbox (VNPay/MoMo sandbox hoặc Stripe test mode); cập nhật trạng thái Paid/Unpaid. | M |
| FR-31 | Hóa đơn quá hạn: khóa upload (chỉ cho phép tải xuống) hoặc tạm khóa tài khoản. | S |
| FR-32 | Xuất hóa đơn PDF. | C |
| FR-33 | Lịch sử giao dịch thanh toán. | S |

### 3.7 Quản trị (Admin)

| Mã | Yêu cầu | Ưu tiên |
| --- | --- | --- |
| FR-34 | Admin đăng nhập vào trang quản trị riêng. | M |
| FR-35 | Xem, tìm kiếm danh sách người dùng; khóa/mở khóa tài khoản. | M |
| FR-36 | Tạo, sửa, vô hiệu hóa gói dịch vụ và bảng giá. | M |
| FR-37 | Dashboard tổng quan: số người dùng, tổng dung lượng, doanh thu theo tháng. | S |
| FR-38 | Xem và đánh dấu thủ công trạng thái hóa đơn. | C |

## 4. Yêu cầu phi chức năng

### 4.1 Hiệu năng

- NFR-01: Thao tác danh sách tệp phản hồi dưới 2 giây với tối đa 1.000 tệp mỗi thư mục.
- NFR-02: Upload/download không đi qua backend khi dùng presigned URL để tránh nghẽn băng thông.
- NFR-03: Hỗ trợ tối thiểu 20 người dùng đồng thời trong buổi demo.
- NFR-04: Hỗ trợ upload tệp lớn (tối thiểu 1 GB) bằng multipart upload.

### 4.2 Bảo mật

- NFR-05: Toàn bộ giao tiếp qua HTTPS (chứng chỉ Let's Encrypt hoặc self-signed).
- NFR-06: JWT có thời hạn; phân quyền theo vai trò (User/Admin) ở backend.
- NFR-07: Storage engine không mở public ra Internet; chỉ backend và presigned URL truy cập được.
- NFR-08: Security Group chỉ mở các cổng cần thiết (80/443, SSH giới hạn IP).
- NFR-09: Chống các lỗi phổ biến: SQL injection, XSS, kiểm tra loại và kích thước tệp.
- NFR-10: Không commit secret/khóa vào Git; dùng biến môi trường.

### 4.3 Độ tin cậy và khả năng phục hồi

- NFR-11: Dữ liệu người dùng lưu trên ổ EBS riêng; có script sao lưu cơ sở dữ liệu định kỳ ra S3 hoặc nơi lưu ngoài.
- NFR-12: Toàn bộ hệ thống dựng lại được bằng một lệnh (Docker Compose/Terraform/user-data) trong dưới 30 phút sau khi lab reset.
- NFR-13: Tự khởi động lại container khi lỗi (restart policy).

### 4.4 Khả năng mở rộng

- NFR-14: Backend stateless, có thể chạy nhiều bản sao sau load balancer.
- NFR-15: Storage engine có thể mở rộng từ 1 node lên nhiều node (nếu ngân sách cho phép, ở mức demo).

### 4.5 Khả dụng và dễ sử dụng

- NFR-16: Giao diện responsive, dùng được trên trình duyệt desktop và điện thoại.
- NFR-17: Giao diện tiếng Việt (có thể thêm tiếng Anh).
- NFR-18: Thông báo lỗi rõ ràng, dễ hiểu.

### 4.6 Chi phí

- NFR-19: Tổng chi phí AWS của dự án không vượt khoảng 60% ngân sách Learner Lab, chừa dự phòng cho demo và sự cố.
- NFR-20: Tắt (stop) tài nguyên khi không sử dụng.

### 4.7 Bảo trì

- NFR-21: Mã nguồn quản lý bằng Git, có README hướng dẫn cài đặt và chạy.
- NFR-22: API có tài liệu (OpenAPI/Swagger).

## 5. Giao diện bên ngoài

### 5.1 Giao diện người dùng

Các màn hình chính: Trang chủ/Bảng giá, Đăng ký, Đăng nhập, Trình quản lý tệp (File Manager), Chia sẻ, Gói dịch vụ & Usage, Hóa đơn & Thanh toán, Hồ sơ, và các trang Admin (Người dùng, Gói dịch vụ, Dashboard).

### 5.2 Giao diện phần mềm

- Backend giao tiếp với storage engine qua S3 API (SDK boto3 / AWS SDK).
- Backend giao tiếp cơ sở dữ liệu qua ORM (SQLAlchemy/Prisma/TypeORM/JPA).
- Cổng thanh toán sandbox qua REST API và webhook/callback.
- SMTP bên ngoài để gửi email.

### 5.3 Giao diện API (tóm tắt)

| Nhóm | Endpoint ví dụ |
| --- | --- |
| Auth | POST /auth/register, POST /auth/login, GET /auth/me |
| Files | GET /files, POST /files/upload-url, GET /files/{id}/download-url, DELETE /files/{id} |
| Folders | POST /folders, PATCH /folders/{id} |
| Share | POST /shares, DELETE /shares/{id}, GET /s/{token} |
| Plans | GET /plans, POST /subscription/change |
| Usage | GET /usage, GET /usage/history |
| Billing | GET /invoices, GET /invoices/{id}, POST /invoices/{id}/pay, POST /payments/callback |
| Admin | GET /admin/users, PATCH /admin/users/{id}, CRUD /admin/plans, GET /admin/stats |

## 6. Kiến trúc triển khai (mức tổng quan)

- **Tầng giao diện:** Nginx/Traefik làm reverse proxy, phục vụ frontend (React/Next.js) và chuyển tiếp API.
- **Tầng ứng dụng:** Backend (FastAPI/NestJS/Spring Boot) chạy trong Docker; job nền (cron/Celery) cho metering và billing.
- **Tầng dữ liệu:** PostgreSQL lưu người dùng, gói, usage, hóa đơn; MinIO/Garage lưu dữ liệu tệp, dùng EBS gp3.
- **Hạ tầng AWS:** 1-2 EC2 (t3.small/t3.medium) trong VPC, public subnet, Security Group chặt; tùy chọn Application Load Balancer và node storage thứ hai để minh họa khả năng mở rộng.
- **Giám sát (tùy chọn):** CloudWatch hoặc Prometheus + Grafana.

## 7. Mô hình dữ liệu sơ bộ

| Bảng | Thuộc tính chính |
| --- | --- |
| users | id, email, password_hash, full_name, role, status, created_at |
| plans | id, name, quota_gb, price_month, price_per_extra_gb, price_per_egress_gb, is_active |
| subscriptions | id, user_id, plan_id, start_date, end_date, status |
| files | id, user_id, parent_id, name, is_folder, size, object_key, content_type, deleted_at, created_at |
| shares | id, file_id, token, expires_at, password_hash, created_at |
| usage_daily | id, user_id, date, storage_bytes, egress_bytes, request_count |
| invoices | id, user_id, period_start, period_end, amount, status, due_date |
| invoice_items | id, invoice_id, description, quantity, unit_price, amount |
| payments | id, invoice_id, provider, transaction_ref, amount, status, paid_at |

## 8. Use case chính

### UC-01 Đăng ký tài khoản
- **Tác nhân:** Khách.
- **Tiền điều kiện:** Chưa có tài khoản với email này.
- **Luồng chính:** Nhập thông tin → hệ thống kiểm tra hợp lệ → tạo user, tạo không gian lưu trữ, gán gói Free → thông báo thành công/gửi email xác nhận.
- **Ngoại lệ:** Email đã tồn tại; mật khẩu yếu.

### UC-02 Tải tệp lên
- **Tác nhân:** Người dùng.
- **Tiền điều kiện:** Đã đăng nhập, còn quota, tài khoản không bị khóa.
- **Luồng chính:** Chọn tệp → backend kiểm tra quota → cấp presigned URL → trình duyệt upload trực tiếp lên storage → backend cập nhật metadata và usage.
- **Ngoại lệ:** Vượt quota; tệp lỗi/đứt kết nối; tài khoản bị khóa do nợ hóa đơn.

### UC-03 Chia sẻ tệp
- **Tác nhân:** Người dùng.
- **Luồng chính:** Chọn tệp → tạo liên kết kèm hạn dùng → người nhận mở liên kết và tải tệp; egress được tính cho chủ sở hữu.

### UC-04 Nâng cấp gói
- **Tác nhân:** Người dùng.
- **Luồng chính:** Xem bảng giá → chọn gói mới → xác nhận → cập nhật subscription và quota; hóa đơn phản ánh thay đổi.

### UC-05 Sinh hóa đơn và thanh toán
- **Tác nhân:** Hệ thống (job định kỳ), Người dùng.
- **Luồng chính:** Cuối chu kỳ, job tổng hợp usage → tính phí gói + phí vượt mức → tạo hóa đơn → người dùng chọn thanh toán → chuyển sang cổng sandbox → callback xác nhận → hóa đơn chuyển sang Paid.
- **Ngoại lệ:** Thanh toán thất bại/hủy; quá hạn thanh toán.

### UC-06 Quản trị người dùng và gói
- **Tác nhân:** Admin.
- **Luồng chính:** Đăng nhập admin → xem danh sách người dùng → khóa/mở khóa; tạo/sửa gói dịch vụ.

## 9. Quy tắc nghiệp vụ và công thức tính phí (đề xuất)

| Gói | Dung lượng | Phí tháng |
| --- | --- | --- |
| Free | 1 GB | 0 |
| Basic | 20 GB | 50.000 VND |
| Pro | 100 GB | 200.000 VND |

- Phí vượt dung lượng: 2.000 VND mỗi GB mỗi tháng (tính theo dung lượng trung bình ngày trong tháng).
- Phí egress: miễn phí 5 GB đầu, sau đó 1.000 VND mỗi GB.
- Gói Free không cho phép vượt quota (chặn upload); gói trả phí cho phép vượt mức và tính phí.
- **Tổng hóa đơn** = phí gói + phí vượt dung lượng + phí egress vượt mức.
- Các con số trên chỉ là ví dụ, nhóm điều chỉnh khi chốt thiết kế.

## 10. Tiêu chí nghiệm thu

- Demo trọn luồng: đăng ký → đăng nhập → upload/download/chia sẻ → xem usage → sinh hóa đơn → thanh toán sandbox.
- Chứng minh cô lập dữ liệu giữa hai người dùng khác nhau.
- Chứng minh chặn upload khi vượt quota.
- Dựng lại hệ thống từ đầu bằng script trên môi trường AWS mới.
- Có báo cáo kiến trúc, tài liệu SRS, hướng dẫn cài đặt và mã nguồn trên Git.

## 11. Rủi ro

| Rủi ro | Giảm thiểu |
| --- | --- |
| Lab reset làm mất tài nguyên | Docker Compose + script dựng lại; backup DB và cấu hình ra Git/S3 |
| Hết ngân sách AWS | Dùng instance nhỏ, stop khi không dùng, theo dõi chi phí hằng ngày |
| Cổng thanh toán sandbox cấu hình phức tạp | Làm sớm ở tuần 2; có phương án dự phòng là thanh toán giả lập nội bộ |
| Trễ tiến độ | Chỉ làm mục M trước, mục S/C chỉ làm khi còn thời gian |
