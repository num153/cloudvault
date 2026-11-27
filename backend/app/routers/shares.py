from fastapi import APIRouter

router = APIRouter(prefix="/shares", tags=["File Sharing"])

@router.get("/ping")
def ping():
    return {"module": "shares", "status": "ready"}
