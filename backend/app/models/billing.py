from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, BigInteger, DateTime, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from app.core.database import Base

class Plan(Base):
    __tablename__ = "plans"

    id = Column(String(50), primary_key=True) # free, basic, pro
    name = Column(String(50), nullable=False)
    quota_gb = Column(Integer, nullable=False)
    price_month = Column(Numeric(12, 2), default=0)
    price_per_extra_gb = Column(Numeric(12, 2), default=0)
    price_per_egress_gb = Column(Numeric(12, 2), default=0)
    is_active = Column(Boolean, default=True)

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

class UsageDaily(Base):
    __tablename__ = "usage_daily"

    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    date = Column(DateTime, nullable=False)
    storage_bytes = Column(BigInteger, default=0)
    egress_bytes = Column(BigInteger, default=0)
    request_count = Column(Integer, default=0)

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

class InvoiceItem(Base):
    __tablename__ = "invoice_items"

    id = Column(String(36), primary_key=True)
    invoice_id = Column(String(36), ForeignKey("invoices.id"), nullable=False)
    description = Column(String(255), nullable=False)
    quantity = Column(Integer, default=1)
    unit_price = Column(Numeric(12, 2), default=0)
    amount = Column(Numeric(12, 2), default=0)

    invoice = relationship("Invoice", back_populates="items")

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
