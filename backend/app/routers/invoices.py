from fastapi import APIRouter

router = APIRouter(prefix="/invoices", tags=["Billing & Invoices"])

@router.get("/ping")
def ping():
    return {"module": "invoices", "status": "ready"}
