# app/dependencies/database.py
from typing import Generator
from app.db.session import SessionLocal 

def get_db() -> Generator:
    """
    Crea una sesión de base de datos nueva para cada petición
    y la cierra cuando la petición termina.
    """
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()