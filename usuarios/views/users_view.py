from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..models.db import SessionLocal
from ..models.models import UserCreate, UserOut, User
from ..logic import users_logic, auth

router = APIRouter()


# ---- Dependencia de DB ----
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---- ENDPOINT: Registrar usuario ----
@router.post("/register", response_model=UserOut)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    created = users_logic.create_user(db, user)
    return created


# ---- ENDPOINT: Login ----
@router.post("/login")
def login(data: dict, db: Session = Depends(get_db)):

    username = data.get("username")
    password = data.get("password")

    user = users_logic.authenticate_user(db, username, password)
    if not user:
        raise HTTPException(401, "Credenciales inválidas")

    token = users_logic.generate_token(user)
    return {"access_token": token, "type": "bearer"}

@router.get("/users")
def get_all_users(user = Depends(auth.require_role("admin")), db: Session = Depends(get_db)):
    return db.query(User).all()
