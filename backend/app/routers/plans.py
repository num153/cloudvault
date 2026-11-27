from fastapi import APIRouter

router = APIRouter(prefix="/plans", tags=["Service Plans"])

@router.get("/ping")
def ping():
    return {"module": "plans", "status": "ready"}
