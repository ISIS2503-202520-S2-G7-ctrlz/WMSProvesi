# Models for the bodegas microservice

from enum import Enum
from pydantic import BaseModel, Field, ConfigDict
from typing import List
from models.db import PyObjectId


class BodegaType(str, Enum):
    Central = "central"
    Regional = "regional"
    Transito = "transito"


class Bodega(BaseModel):
    code: str = Field(..., description="Código único de la bodega")
    name: str = Field(..., description="Nombre descriptivo de la bodega")
    city: str = Field(..., description="Ciudad donde se encuentra la bodega")
    address: str = Field(..., description="Dirección de la bodega")
    capacity: int = Field(..., description="Capacidad máxima de almacenamiento")
    active: bool = Field(default=True, description="Indica si la bodega está activa")
    type: BodegaType = Field(..., description="Tipo de bodega")
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "code": "BOD-001",
                "name": "Bodega Central Norte",
                "city": "Bogotá",
                "address": "Calle 123 #45-67",
                "capacity": 5000,
                "active": True,
                "type": BodegaType.Central,
            }
        },
    )


class BodegaOut(Bodega):
    id: PyObjectId = Field(alias="_id", default=None, serialization_alias="id")
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "64b8f0f2e1b1c8a1f0d4e8b5",
                "code": "BOD-001",
                "name": "Bodega Central Norte",
                "city": "Bogotá",
                "address": "Calle 123 #45-67",
                "capacity": 5000,
                "active": True,
                "type": BodegaType.Central,
            }
        },
    )


class BodegaCollection(BaseModel):
    # A collection of bodegas
    bodegas: List[BodegaOut] = Field(...)