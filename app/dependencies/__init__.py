from typing import Generator
from app.db.session import SessionLocal

# Esta función se usa en CADA endpoint para abrir/cerrar conexión DB
def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()