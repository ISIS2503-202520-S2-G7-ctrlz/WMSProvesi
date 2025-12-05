from sqlalchemy import Column, Integer, String
from pydantic import BaseModel
from .db import Base


# --- Modelo SQLAlchemy ---
class User(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String, default="user")


# --- Esquemas Pydantic ---
class UserCreate(BaseModel):
    username: str
    password: str
    role: str = "user"


class UserOut(BaseModel):
    id: int
    username: str
    role: str

    class Config:
        from_attributes = True