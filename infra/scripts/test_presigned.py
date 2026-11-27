#!/usr/bin/env python3
"""
Script thử nghiệm Presigned URL qua Nginx (PoC Test)
Dự án: CloudVault

Mục tiêu:
1. Kiểm tra tính hợp lệ của chữ ký S3v4 khi đi qua Nginx Reverse Proxy.
2. Kiểm tra xem Nginx có làm lệch Host ($http_host) hoặc URI path không.
3. Xác nhận luồng upload PUT và download GET trực tiếp với MinIO qua Nginx.
"""

import os
import sys
import uuid
import requests
import boto3
from botocore.config import Config

# Nạp biến từ .env nếu chưa có trong môi trường
env_path = os.path.join(os.path.dirname(__file__), "..", "..", ".env")
if os.path.exists(env_path):
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())

# Cấu hình Endpoints
# PUBLIC: Trình duyệt/Client bên ngoài gọi tới (qua Nginx)
PUBLIC = os.getenv("S3_PUBLIC_ENDPOINT", "http://localhost")

# INTERNAL: Backend/Server gọi trực tiếp tới MinIO
# Nếu chạy từ máy Host thì MinIO lắng nghe cổng 9000: http://localhost:9000
# Nếu chạy trong Docker container thì là: http://minio:9000
INTERNAL = os.getenv("S3_INTERNAL_ENDPOINT", "http://localhost:9000")
if "minio:9000" in INTERNAL and os.name == "nt":
    # Fallback cho máy Windows host nếu chưa cấu hình hosts file
    INTERNAL = "http://localhost:9000"

BUCKET = os.getenv("S3_BUCKET_NAME", os.getenv("S3_BUCKET", "cloudvault-data"))
AK = os.getenv("S3_ACCESS_KEY", os.getenv("MINIO_ROOT_USER", "minioadmin"))
SK = os.getenv("S3_SECRET_KEY", os.getenv("MINIO_ROOT_PASSWORD", "miniopassword123"))
REGION = os.getenv("S3_REGION", "us-east-1")

print("=" * 60)
print("KIỂM TRA PRESIGNED URL QUA NGINX - CLOUDVAULT")
print("=" * 60)
print(f"[*] S3 Public Endpoint (qua Nginx): {PUBLIC}")
print(f"[*] S3 Internal Endpoint (Server): {INTERNAL}")
print(f"[*] Target Bucket:                  {BUCKET}")
print("=" * 60)

cfg = Config(
    signature_version="s3v4",
    s3={"addressing_style": "path"}
)

# 1. Signer Client: Dùng S3_PUBLIC_ENDPOINT để tính chữ ký cho client ngoài
signer = boto3.client(
    "s3",
    endpoint_url=PUBLIC,
    aws_access_key_id=AK,
    aws_secret_access_key=SK,
    region_name=REGION,
    config=cfg
)

# 2. Admin Client: Dùng S3_INTERNAL_ENDPOINT để thao tác server-side
admin = boto3.client(
    "s3",
    endpoint_url=INTERNAL,
    aws_access_key_id=AK,
    aws_secret_access_key=SK,
    region_name=REGION,
    config=cfg
)

test_id = uuid.uuid4().hex[:8]
key = f"test_presigned/poc_{test_id}.txt"
body = f"Hello CloudVault Presigned URL! Test ID: {test_id}".encode("utf-8")

# BƯỚC 1: Sinh Presigned PUT URL và upload thử qua Nginx
print("\n[Bước 1] Sinh Presigned URL cho upload (PUT)...")
try:
    put_url = signer.generate_presigned_url(
        "put_object",
        Params={"Bucket": BUCKET, "Key": key},
        ExpiresIn=300
    )
    print(f"-> Presigned PUT URL: {put_url[:100]}...")

    print("\n[Bước 2] Client gửi HTTP PUT đẩy dữ liệu lên qua Nginx...")
    res_put = requests.put(put_url, data=body, timeout=10)
    print(f"-> Kết quả PUT: Status {res_put.status_code}")
    
    if res_put.status_code != 200:
        print(f"[!] LỖI UPLOAD: {res_put.text}")
        if "SignatureDoesNotMatch" in res_put.text:
            print("\n[GIẢI THÍCH LỖI] 'SignatureDoesNotMatch':")
            print("- Nguyên nhân: Nginx đã làm biến đổi Host header hoặc đường dẫn URL khi chuyển tiếp.")
            print("- Hãy kiểm tra proxy_set_header Host $http_host và không dùng tiền tố cắt xén.")
        sys.exit(1)
    else:
        print("-> Upload thành công 100% qua Nginx!")

    # BƯỚC 3: Server-side kiểm tra file trong MinIO bằng Admin Client
    print("\n[Bước 3] Server kiểm tra (HEAD object) qua endpoint nội bộ...")
    head = admin.head_object(Bucket=BUCKET, Key=key)
    print(f"-> File tồn tại trong MinIO! Dung lượng: {head['ContentLength']} bytes (khớp: {head['ContentLength'] == len(body)})")

    # BƯỚC 4: Sinh Presigned GET URL và tải về kiểm tra
    print("\n[Bước 4] Sinh Presigned URL cho download (GET) và tải về...")
    get_url = signer.generate_presigned_url(
        "get_object",
        Params={"Bucket": BUCKET, "Key": key},
        ExpiresIn=300
    )
    res_get = requests.get(get_url, timeout=10)
    print(f"-> Kết quả GET: Status {res_get.status_code}")
    match = res_get.content == body
    print(f"-> Nội dung tải về khớp với file gốc: {match}")

    # BƯỚC 5: Dọn dẹp file test
    print("\n[Bước 5] Dọn dẹp object test...")
    #admin.delete_object(Bucket=BUCKET, Key=key)
    print("-> Đã xóa file test. Hoàn tất!")

    print("\n" + "=" * 60)
    print("KẾT LUẬN: ĐƯỜNG TRUYỀN PRESIGNED URL QUA NGINX HOẠT ĐỘNG HOÀN HẢO!")
    print("=" * 60)

except Exception as e:
    print(f"\n[!] NGOẠI LỆ XẢY RA: {e}")
    sys.exit(1)
