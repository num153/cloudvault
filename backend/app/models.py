from sqlalchemy import Column, Integer, String, Boolean, BigInteger, DateTime, ForeignKey, Numeric
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()

# 1. Bảng Người dùng (users)
class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(String(20), default="user") # 'user' | 'admin'
    status = Column(String(20), default="active") # 'active' | 'suspended'
    created_at = Column(DateTime, default=datetime.utcnow)

    subscriptions = relationship("Subscription", back_populates="user")
    files = relationship("FileItem", back_populates="user")
    invoices = relationship("Invoice", back_populates="user")

# 2. Bảng Gói cước (plans)
class Plan(Base):
    __tablename__ = "plans"

    id = Column(String(50), primary_key=True)
    name = Column(String(50), nullable=False) # Free, Basic, Pro
    quota_gb = Column(Integer, nullable=False)
    price_month = Column(Numeric(12, 2), default=0)
    price_per_extra_gb = Column(Numeric(12, 2), default=0)
    price_per_egress_gb = Column(Numeric(12, 2), default=0)
    is_active = Column(Boolean, default=True)

# 3. Bảng Thuê bao gói cước (subscriptions)
class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    plan_id = Column(String(50), ForeignKey("plans.id"), nullable=False)
    start_date = Column(DateTime, default=datetime.utcnow)
    end_date = Column(DateTime, nullable=True)
    status = Column(String(20), default="active") # 'active' | 'cancelled' | 'expired'

    user = relationship("User", back_populates="subscriptions")
    plan = relationship("Plan")

# 4. Bảng Metadata Tệp & Thư mục (files)
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
    deleted_at = Column(DateTime, nullable=True) # Thùng rác xóa mềm
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="files")
    shares = relationship("Share", back_populates="file")

# 5. Bảng Chia sẻ tệp (shares)
class Share(Base):
    __tablename__ = "shares"

    id = Column(String(36), primary_key=True)
    file_id = Column(String(36), ForeignKey("files.id"), nullable=False)
    token = Column(String(64), unique=True, nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False)
    password_hash = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    file = relationship("FileItem", back_populates="shares")

# 6. Bảng Đo lường mức sử dụng hàng ngày (usage_daily)
class UsageDaily(Base):
    __tablename__ = "usage_daily"

    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    date = Column(DateTime, nullable=False)
    storage_bytes = Column(BigInteger, default=0)
    egress_bytes = Column(BigInteger, default=0)
    request_count = Column(Integer, default=0)

# 7. Bảng Hóa đơn (invoices)
class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    amount = Column(Numeric(12, 2), default=0)
    status = Column(String(20), default="UNPAID") # 'UNPAID' | 'PAID' | 'OVERDUE'
    due_date = Column(DateTime, nullable=False)

    user = relationship("User", back_populates="invoices")
    items = relationship("InvoiceItem", back_populates="invoice")
    payments = relationship("Payment", back_populates="invoice")

# 8. Bảng Chi tiết mục hóa đơn (invoice_items)
class InvoiceItem(Base):
    __tablename__ = "invoice_items"

    id = Column(String(36), primary_key=True)
    invoice_id = Column(String(36), ForeignKey("invoices.id"), nullable=False)
    description = Column(String(255), nullable=False)
    quantity = Column(Integer, default=1)
    unit_price = Column(Numeric(12, 2), default=0)
    amount = Column(Numeric(12, 2), default=0)

    invoice = relationship("Invoice", back_populates="items")

# 9. Bảng Giao dịch thanh toán (payments)
class Payment(Base):
    __tablename__ = "payments"

    id = Column(String(36), primary_key=True)
    invoice_id = Column(String(36), ForeignKey("invoices.id"), nullable=False)
    provider = Column(String(50), nullable=False) # 'vnpay' | 'momo' | 'stripe'
    transaction_ref = Column(String(100), nullable=False)
    amount = Column(Numeric(12, 2), default=0)
    status = Column(String(20), default="PENDING") # 'PENDING' | 'SUCCESS' | 'FAILED'
    paid_at = Column(DateTime, nullable=True)

    invoice = relationship("Invoice", back_populates="payments")
