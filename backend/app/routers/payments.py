from fastapi import APIRouter

router = APIRouter(prefix="/payments", tags=["Payment Transactions"])

@router.get("/ping")
def ping():
    return {"module": "payments", "status": "ready"}
