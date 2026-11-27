from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session
import boto3

from app.core.config import settings
from app.core.database import engine, Base, get_db
import app.models  # load all models into Base

from app.routers.auth import router as auth_router
from app.routers.admin import router as admin_router
from app.routers.plans import router as plans_router
from app.routers.files import router as files_router
from app.routers.shares import router as shares_router
from app.routers.usage import router as usage_router
from app.routers.invoices import router as invoices_router
from app.routers.payments import router as payments_router

# Khởi tạo tables nếu chưa có (kết hợp với Alembic)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Backend API cho hệ thống Cloud Data Storage (Điện toán đám mây)",
    version="1.0.0",
    docs_url="/docs",
    openapi_url="/openapi.json"
)

# Cấu hình CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Đăng ký các router nghiệp vụ
app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(plans_router)
app.include_router(files_router)
app.include_router(shares_router)
app.include_router(usage_router)
app.include_router(invoices_router)
app.include_router(payments_router)

@app.on_event("startup")
def on_startup():
    # Tự động seed dữ liệu mẫu (3 gói dịch vụ & admin) nếu chưa có
    try:
        from seed import seed
        seed()
    except Exception as e:
        print(f"[Startup Seed Warning] {e}")

@app.get("/")
def read_root():
    return {
        "status": "online",
        "service": settings.PROJECT_NAME,
        "version": "1.0.0",
        "message": "Backend FastAPI đã sẵn sàng kết nối!"
    }

@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    health_status = {
        "api": "healthy",
        "database": "unknown",
        "minio_storage": "unknown"
    }

    # Kiểm tra PostgreSQL
    try:
        db.execute(text("SELECT 1"))
        health_status["database"] = "connected"
    except Exception as e:
        health_status["database"] = f"error: {str(e)}"

    # Kiểm tra MinIO (nội bộ)
    try:
        s3_client = boto3.client(
            "s3",
            endpoint_url=settings.S3_INTERNAL_ENDPOINT,
            aws_access_key_id=settings.S3_ACCESS_KEY,
            aws_secret_access_key=settings.S3_SECRET_KEY,
            region_name=settings.S3_REGION
        )
        response = s3_client.list_buckets()
        buckets = [b["Name"] for b in response.get("Buckets", [])]
        health_status["minio_storage"] = {
            "status": "connected",
            "buckets": buckets
        }
    except Exception as e:
        health_status["minio_storage"] = f"error: {str(e)}"

    return health_status
