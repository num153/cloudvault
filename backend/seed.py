"""
Script khởi tạo dữ liệu mẫu (Seed Data):
- 3 Gói dịch vụ: Free, Basic, Pro (theo mục 9 SRS)
- 1 Tài khoản Admin mặc định
"""
import uuid
from app.core.database import SessionLocal
from app.core.security import get_password_hash
from app.models.billing import Plan
from app.models.identity import User

def seed():
    db = SessionLocal()
    try:
        # 1. Seed Plans
        plans_data = [
            {
                "id": "free",
                "name": "Free",
                "quota_gb": 1,
                "price_month": 0,
                "price_per_extra_gb": 0,
                "price_per_egress_gb": 0,
                "is_active": True
            },
            {
                "id": "basic",
                "name": "Basic",
                "quota_gb": 20,
                "price_month": 50000,
                "price_per_extra_gb": 2000,
                "price_per_egress_gb": 1000,
                "is_active": True
            },
            {
                "id": "pro",
                "name": "Pro",
                "quota_gb": 100,
                "price_month": 200000,
                "price_per_extra_gb": 2000,
                "price_per_egress_gb": 1000,
                "is_active": True
            }
        ]

        for p_data in plans_data:
            existing_plan = db.query(Plan).filter(Plan.id == p_data["id"]).first()
            if not existing_plan:
                plan = Plan(**p_data)
                db.add(plan)
                print(f"[Seed] Created Plan: {p_data['name']}")
            else:
                print(f"[Seed] Plan {p_data['name']} already exists.")

        # 2. Seed Default Admin User
        admin_email = "admin@cloudvault.com"
        existing_admin = db.query(User).filter(User.email == admin_email).first()
        if not existing_admin:
            admin_user = User(
                id=f"usr_{uuid.uuid4().hex[:12]}",
                email=admin_email,
                password_hash=get_password_hash("Admin@123"),
                full_name="System Administrator",
                role="admin",
                status="active"
            )
            db.add(admin_user)
            print(f"[Seed] Created Default Admin: {admin_email} (Pass: Admin@123)")
        else:
            print(f"[Seed] Admin user {admin_email} already exists.")

        db.commit()
        print("[Seed] Seed data finished successfully!")
    except Exception as e:
        db.rollback()
        print(f"[Seed Error] {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed()
