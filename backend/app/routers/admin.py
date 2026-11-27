from fastapi import APIRouter

router = APIRouter(prefix="/admin", tags=["Admin Management"])

@router.get("/ping")
def ping():
    return {"module": "admin", "status": "ready"}
