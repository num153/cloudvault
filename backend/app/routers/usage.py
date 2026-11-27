from fastapi import APIRouter

router = APIRouter(prefix="/usage", tags=["Resource Metering & Usage"])

@router.get("/ping")
def ping():
    return {"module": "usage", "status": "ready"}
