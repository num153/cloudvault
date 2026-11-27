from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field

class UserRegisterRequest(BaseModel):
    email: EmailStr = Field(..., example="user@example.com")
    password: str = Field(..., min_length=6, description="Mật khẩu tối thiểu 6 ký tự", example="Password123!")
    full_name: str = Field(..., min_length=1, description="Họ và tên người dùng", example="Nguyen Van A")

class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    role: str
    status: str
    storage_prefix: str
    created_at: datetime
    current_plan: Optional[str] = "Free"

    class Config:
        from_attributes = True

class RegisterResponse(BaseModel):
    message: str
    user: UserResponse
