from fastapi import APIRouter
from app.api.routes import upload  

router = APIRouter()
router.include_router(upload.router)

@router.get("/health")
def health_check():
    return {"status": "OK"}