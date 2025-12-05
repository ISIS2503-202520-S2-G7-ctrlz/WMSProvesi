from fastapi import FastAPI
from .models.db import Base, engine
from .views.users_view import router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Microservicio Usuarios")

app.include_router(router, prefix="/usuarios")
