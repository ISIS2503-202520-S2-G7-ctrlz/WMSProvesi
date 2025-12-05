from fastapi import APIRouter

from views import bodegas_view

API_PREFIX = "/api"
router = APIRouter()

router.include_router(bodegas_view.router, prefix=bodegas_view.ENDPOINT_NAME)