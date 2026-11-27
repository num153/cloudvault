import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "CloudVault"
    ENVIRONMENT: str = "development"
    
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://cloudvault_user:cloudvault_secure_password_123@postgres:5432/cloudvault_db"
    )

    # MinIO / S3
    S3_INTERNAL_ENDPOINT: str = os.getenv("S3_INTERNAL_ENDPOINT", os.getenv("S3_ENDPOINT", "http://minio:9000"))
    S3_PUBLIC_ENDPOINT: str = os.getenv("S3_PUBLIC_ENDPOINT", "http://localhost")
    S3_ACCESS_KEY: str = os.getenv("S3_ACCESS_KEY", os.getenv("MINIO_ROOT_USER", "minioadmin"))
    S3_SECRET_KEY: str = os.getenv("S3_SECRET_KEY", os.getenv("MINIO_ROOT_PASSWORD", "miniopassword123"))
    S3_BUCKET_NAME: str = os.getenv("S3_BUCKET_NAME", os.getenv("MINIO_DEFAULT_BUCKET", "cloudvault-data"))
    S3_REGION: str = os.getenv("S3_REGION", "us-east-1")

    # JWT Authentication
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "cloudvault_super_secret_jwt_key_default_32chars")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    @property
    def sync_database_url(self) -> str:
        url = self.DATABASE_URL
        if url.startswith("postgresql://"):
            url = url.replace("postgresql://", "postgresql+psycopg2://", 1)
        return url

    class Config:
        env_file = ".env"
        extra = "allow"

settings = Settings()
