from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.database import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)

def get_current_user(
    db: Session = Depends(get_db),
    token: Optional[str] = Depends(oauth2_scheme)
):
    """
    Dependency get_current_user:
    - Nếu có token hợp lệ: giải mã lấy User từ DB.
    - Nếu chưa có token hoặc token giả trong giai đoạn dev:
      Tự động fallback về Mock User để các router khác test mà không bị chặn.
    """
    from app.models.identity import User

    if token:
        try:
            payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
            user_id: str = payload.get("sub")
            if user_id:
                user = db.query(User).filter(User.id == user_id).first()
                if user:
                    return user
        except JWTError:
            pass # fallback to mock user during dev

    # Tạm thời fallback Mock User để không nghẽn các module khác
    mock_user = db.query(User).filter(User.email == "dev_user@cloudvault.com").first()
    if not mock_user:
        mock_user = User(
            id="usr_mock_dev_01",
            email="dev_user@cloudvault.com",
            full_name="Developer Mock User",
            role="user",
            status="active"
        )
    return mock_user
