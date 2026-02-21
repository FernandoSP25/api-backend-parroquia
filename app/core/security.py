from datetime import datetime, timedelta
from typing import Any, Union
from jose import jwt
import bcrypt  # <--- Usamos la librería directa

from app.core.config import settings

def create_access_token(subject: Union[str, Any], expires_delta: timedelta = None) -> str:
    """
    Crea el token JWT (Esto se queda igual)
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica si la contraseña coincide con el hash.
    Recibe strings, los convierte a bytes para bcrypt.
    """
    # bcrypt necesita bytes, así que usamos .encode('utf-8')
    return bcrypt.checkpw(
        plain_password.encode('utf-8'), 
        hashed_password.encode('utf-8')
    )

def get_password_hash(password: str) -> str:
    """
    Genera el hash de la contraseña.
    Devuelve un string para guardarlo en la base de datos.
    """
    # 1. Generar Salt y Hash
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    
    # 2. Devolver como string (decodificar bytes) para que PostgreSQL lo acepte
    return hashed.decode('utf-8')

def validate_password(password: str):
    if len(password) < 8:
        raise ValueError("La contraseña debe tener al menos 8 caracteres")
