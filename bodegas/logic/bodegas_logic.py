"""
This module contains the logic for the bodegas app.
Main functions:
- get_bodegas: Get a list of all bodegas
- get_bodega: Get a single bodega
- create_bodega: Create a new bodega
- update_bodega: Update a bodega
- delete_bodega: Delete a bodega
"""

from models.models import Bodega, BodegaCollection
from models.db import bodegas_collection
from pymongo.errors import DuplicateKeyError
from fastapi import HTTPException


async def get_bodegas():
    """
    Get a list of bodegas
    :return: A list of bodegas
    """
    bodegas = await bodegas_collection.find().to_list(1000)
    return BodegaCollection(bodegas=bodegas)


async def get_bodega(bodega_code: str):
    """
    Get a single bodega
    :param bodega_code: The code of the bodega
    :return: The bodega
    """
    if (bodega := await bodegas_collection.find_one({"code": bodega_code})) is not None:
        return bodega

    raise HTTPException(
        status_code=404, detail=f"Bodega with code {bodega_code} not found"
    )


async def create_bodega(bodega: Bodega):
    """
    Insert a new bodega record.
    """

    try:
        new_bodega = await bodegas_collection.insert_one(
            bodega.model_dump(by_alias=True, exclude=["id"])
        )
        created_bodega = await bodegas_collection.find_one({"_id": new_bodega.inserted_id})
        return created_bodega

    except DuplicateKeyError:
        raise HTTPException(
            status_code=409, detail=f"Bodega with code {bodega.code} already exists"
        )


async def update_bodega(bodega_code: str, bodega: Bodega):
    """
    Update a bodega
    :param bodega_code: The code of the bodega
    :param bodega: The bodega data
    :return: The updated bodega
    """

    try:
        update_result = await bodegas_collection.update_one(
            {"code": bodega_code},
            {"$set": bodega.model_dump(by_alias=True, exclude=["id"])},
        )
        if update_result.modified_count == 1:
            if (
                updated_bodega := await bodegas_collection.find_one({"code": bodega.code})
            ) is not None:
                return updated_bodega
    except DuplicateKeyError:
        raise HTTPException(
            status_code=409, detail=f"Bodega with code {bodega.code} already exists"
        )

    raise HTTPException(
        status_code=404,
        detail=f"Bodega with code {bodega_code} not found or no updates were made",
    )


async def delete_bodega(bodega_code: str):
    """
    Delete a bodega
    :param bodega_code: The code of the bodega
    """
    delete_result = await bodegas_collection.delete_one({"code": bodega_code})

    if delete_result.deleted_count == 1:
        return

    raise HTTPException(
        status_code=404, detail=f"Bodega with code {bodega_code} not found"
    )