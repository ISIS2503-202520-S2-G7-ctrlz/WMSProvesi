import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


USUARIOS_HOST = os.getenv("USUARIOS_DB_HOST", "localhost")
DATABASE_URL = f"postgresql://provesi_user:Isis2503@{USUARIOS_HOST}:5432/usuarios_db"


engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()