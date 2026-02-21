from pydantic import BaseModel, EmailStr
from typing import List, Optional

# --- INPUTS (Lo que recibimos) ---

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

# --- INTERNAL (Lo que usa el Backend internamente) ---

# ¡IMPORTANTE! No borres esto. 
# Lo usará tu función 'get_current_user' para leer el token desencriptado.
class TokenData(BaseModel):
    id: Optional[str] = None # Guardamos el ID (sub) aquí
    email: Optional[str] = None

# --- OUTPUTS (Lo que enviamos al Frontend) ---

# 1. El objeto anidado con los datos del usuario
class UserInfo(BaseModel):
    email: str
    nombre: str
    roles: List[str]  # Ejemplo: ["ADMIN", "CATEQUISTA"]

# 2. La respuesta completa del Login
class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserInfo  # <--- Aquí incrustamos el objeto de arriba