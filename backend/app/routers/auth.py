import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import boto3

from app.core.config import settings
from app.core.database import get_db
from app.core.security import get_password_hash
from app.models.identity import User
from app.models.billing import Plan, Subscription
from app.schemas.auth import UserRegisterRequest, RegisterResponse, UserResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.get("/ping")
def ping():
    return {"module": "auth", "status": "ready"}

@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Đăng ký tài khoản người dùng mới (FR-01, FR-02, FR-03)"
)
def register(
    data: UserRegisterRequest,
    db: Session = Depends(get_db)
):
    # 1. Kiểm tra email đã tồn tại chưa
    existing_user = db.query(User).filter(User.email == data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email này đã được sử dụng. Vui lòng chọn email khác."
        )

    # 2. Kiểm tra gói dịch vụ Free mặc định
    free_plan = db.query(Plan).filter(Plan.id == "free").first()
    if not free_plan:
        # Nếu chưa seed thì tạo tự động gói Free
        free_plan = Plan(
            id="free",
            name="Free",
            quota_gb=1,
            price_month=0,
            price_per_extra_gb=0,
            price_per_egress_gb=0,
            is_active=True
        )
        db.add(free_plan)
        db.flush()

    # 3. Tạo ID và băm mật khẩu
    user_id = f"usr_{uuid.uuid4().hex[:12]}"
    new_user = User(
        id=user_id,
        email=data.email,
        password_hash=get_password_hash(data.password),
        full_name=data.full_name,
        role="user",
        status="active",
        created_at=datetime.utcnow()
    )
    db.add(new_user)

    # 4. Tự động gán gói Free qua Subscription
    sub_id = f"sub_{uuid.uuid4().hex[:12]}"
    new_sub = Subscription(
        id=sub_id,
        user_id=user_id,
        plan_id=free_plan.id,
        start_date=datetime.utcnow(),
        status="active"
    )
    db.add(new_sub)

    # 5. Khởi tạo không gian lưu trữ riêng (Storage Prefix: user_<id>/) trên MinIO
    try:
        s3 = boto3.client(
            "s3",
            endpoint_url=settings.S3_INTERNAL_ENDPOINT,
            aws_access_key_id=settings.S3_ACCESS_KEY,
            aws_secret_access_key=settings.S3_SECRET_KEY,
            region_name=settings.S3_REGION
        )
        # Tạo object rỗng có key kết thúc bằng / để định hình prefix
        s3.put_object(
            Bucket=settings.S3_BUCKET_NAME,
            Key=new_user.storage_prefix
        )
    except Exception as s3_err:
        print(f"[Warning] S3 prefix creation for {new_user.storage_prefix}: {s3_err}")

    # 6. Commit Database
    db.commit()
    db.refresh(new_user)

    return RegisterResponse(
        message="Đăng ký tài khoản thành công!",
        user=UserResponse(
            id=new_user.id,
            email=new_user.email,
            full_name=new_user.full_name,
            role=new_user.role,
            status=new_user.status,
            storage_prefix=new_user.storage_prefix,
            created_at=new_user.created_at,
            current_plan=free_plan.name
        )
    )
