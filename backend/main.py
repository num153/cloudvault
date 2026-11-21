import os
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker, Session
import boto3

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://cloudvault_user:cloudvault_secure_password_123@postgres:5432/cloudvault_db")
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://", 1)
S3_ENDPOINT = os.getenv("S3_ENDPOINT", "http://minio:9000")
S3_ACCESS_KEY = os.getenv("S3_ACCESS_KEY", "minioadmin")
S3_SECRET_KEY = os.getenv("S3_SECRET_KEY", "miniopassword123")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME", "cloudvault-data")

app = FastAPI(
    title="CloudVault API",
    description="Backend API cho hệ thống Cloud Data Storage (Điện toán đám mây)",
    version="1.0.0",
    docs_url="/docs",
    openapi_url="/openapi.json"
)

# Cấu hình CORS cho phép Frontend truy cập
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Kết nối Database Engine (lazy check)
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {
        "status": "online",
        "service": "CloudVault API",
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

    # Kiểm tra MinIO
    try:
        s3_client = boto3.client(
            "s3",
            endpoint_url=S3_ENDPOINT,
            aws_access_key_id=S3_ACCESS_KEY,
            aws_secret_access_key=S3_SECRET_KEY
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
