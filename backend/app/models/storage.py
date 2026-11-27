from datetime import datetime
from sqlalchemy import Column, String, Boolean, BigInteger, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class FileItem(Base):
    __tablename__ = "files"

    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    parent_id = Column(String(36), ForeignKey("files.id"), nullable=True)
    name = Column(String(255), nullable=False)
    is_folder = Column(Boolean, default=False)
    size = Column(BigInteger, default=0) # Bytes
    object_key = Column(String(500), nullable=True) # S3 prefix: user_<id>/<uuid>
    content_type = Column(String(100), nullable=True)
    deleted_at = Column(DateTime, nullable=True) # Xóa mềm (Thùng rác)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="files")
    shares = relationship("Share", back_populates="file")

class Share(Base):
    __tablename__ = "shares"

    id = Column(String(36), primary_key=True)
    file_id = Column(String(36), ForeignKey("files.id"), nullable=False)
    token = Column(String(64), unique=True, nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False)
    password_hash = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    file = relationship("FileItem", back_populates="shares")
