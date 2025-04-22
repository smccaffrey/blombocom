from fastapi import APIRouter

from blombo.api.v1.endpoints import text

router = APIRouter()

# Include endpoint routers
router.include_router(text.router, prefix="/text", tags=["text"]) 