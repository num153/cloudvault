from fastapi import APIRouter

router = APIRouter(prefix="/files", tags=["Files Management"])

@router.get("/ping")
def ping():
    return {"module": "files", "status": "ready"}
