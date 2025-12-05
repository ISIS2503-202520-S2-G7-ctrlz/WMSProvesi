# models/db.py
import os
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic.functional_validators import BeforeValidator
from typing_extensions import Annotated

# -----------------------------
# Configuración del cliente
# -----------------------------
MONGO_HOST = os.getenv("BODEGAS_DB_HOST", "localhost")

MONGO_URI = (
    f"mongodb://provesi_user:isis2503@{MONGO_HOST}:27017/provesi_db"
    "?authSource=provesi_db"
)

client = None


async def set_bodegas_db():
    """
    Inicializa el cliente, base de datos y colección.
    Se llama una sola vez en el startup.
    """
    global client, database, bodegas_collection

    if client is None:
        client = AsyncIOMotorClient(MONGO_URI)

    database = client["provesi_db"]
    bodegas_collection = database["bodegas"]

    # Crear índice único
    await bodegas_collection.create_index("code", unique=True)


# Representa un ObjectId en el modelo Pydantic
PyObjectId = Annotated[str, BeforeValidator(str)]
