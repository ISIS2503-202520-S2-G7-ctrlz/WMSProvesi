from fastapi import APIRouter, status, Body
import logic.bodegas_logic as bodegas_service
from models.models import Bodega, BodegaOut, BodegaCollection

router = APIRouter()
ENDPOINT_NAME = "/bodegas"


@router.get(
    "/",
    response_description="List all bodegas",
    response_model=BodegaCollection,
    status_code=status.HTTP_200_OK,
)
async def get_bodegas():
    return await bodegas_service.get_bodegas()


@router.get(
    "/{bodega_code}",
    response_description="Get a single bodega by its code",
    response_model=BodegaOut,
    status_code=status.HTTP_200_OK,
)
async def get_bodega(bodega_code: str):
    return await bodegas_service.get_bodega(bodega_code)


@router.post(
    "/",
    response_description="Create a new bodega",
    response_model=BodegaOut,
    status_code=status.HTTP_201_CREATED,
)
async def create_bodega(bodega: Bodega = Body(...)):
    return await bodegas_service.create_bodega(bodega)


@router.put(
    "/{bodega_code}",
    response_description="Update a bodega",
    response_model=BodegaOut,
    status_code=status.HTTP_200_OK,
)
async def update_bodega(bodega_code: str, bodega: Bodega = Body(...)):
    return await bodegas_service.update_bodega(bodega_code, bodega)


@router.delete(
    "/{bodega_code}",
    response_description="Delete a bodega",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_bodega(bodega_code: str):
    return await bodegas_service.delete_bodega(bodega_code)