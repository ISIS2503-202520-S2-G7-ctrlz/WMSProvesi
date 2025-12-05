from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError

from ..models.db import get_db
from ..models.models import User

SECRET_KEY = "supersecret"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/usuarios/login")

def get_current_user(token: str = Depends(oauth2_scheme), db=Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        username: str = payload.get("sub")

        if username is None:
            raise HTTPException(status_code=401, detail="Token inválido")

        user = db.query(User).filter(User.username == username).first()
        if user is None:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

        return user

    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido")


def require_role(*roles):
    def role_checker(user = Depends(get_current_user)):
        if user.role not in roles:
            raise HTTPException(status_code=403, detail="No tienes permiso para esta acción")
        return user
    return role_checker
