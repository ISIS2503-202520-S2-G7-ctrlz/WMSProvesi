from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import jwt
from ..models.models import User, UserCreate
from ..models.db import SessionLocal

SECRET_KEY = "supersecret"
ALGORITHM = "HS256"
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# --------------------------
#   UTILIDADES
# --------------------------
def hash_password(password: str):
    return pwd_context.hash(password)


def verify_password(password: str, hashed: str):
    return pwd_context.verify(password, hashed)


def generate_token(user: User):
    payload = {"sub": user.username, "role": user.role}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


# --------------------------
#   CRUD Y LOGIN
# --------------------------
def create_user(db: Session, user_data: UserCreate):
    hashed = hash_password(user_data.password)

    user = User(
        username=user_data.username,
        hashed_password=hashed,
        role=user_data.role
    )

    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, username: str, password: str):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user
