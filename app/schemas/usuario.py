from pydantic import BaseModel, EmailStr
from typing import Optional
from uuid import UUID
from datetime import date, datetime
from typing import List, Any
from pydantic import field_validator 
# --- BASE ---
# Datos comunes que tienen tanto al crear como al leer
class UsuarioBase(BaseModel):
    nombres: str
    apellidos: str
    dni: str
    email: EmailStr         # El email del sistema/login
    email_personal: Optional[EmailStr] = None # El email personal
    activo: bool = True
    fecha_nacimiento: Optional[date] = None
    foto_url: Optional[str] = None

# --- CREATE ---
# Datos necesarios para crear un usuario (incluye password)
class UsuarioCreate(UsuarioBase):
    password: str

# --- UPDATE ---
# Todos opcionales, para actualizar solo lo que se necesite
class UsuarioUpdate(BaseModel):
    nombres: Optional[str] = None
    apellidos: Optional[str] = None
    email_personal: Optional[EmailStr] = None
    dni: Optional[str] = None
    activo: Optional[bool] = None
    password: Optional[str] = None # Si envían esto, se hashea y actualiza
    foto_url: Optional[str] = None
    fecha_nacimiento: Optional[date] = None
    celular: Optional[str] = None

class UsuarioOut(UsuarioBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    
    roles: List[str] = [] 
    celular: Optional[str] = None # Este campo se llenará con el validador

    # 1. Validador para Roles (Ya lo tenías)
    @field_validator('roles', mode='before')
    def procesar_roles(cls, v: Any):
        if not v: return []
        # Si v es una lista de objetos ORM, sacamos el nombre
        return [item.rol.nombre for item in v if item.rol]

    # 2. ✅ NUEVO VALIDADOR PARA CELULAR
    @field_validator('celular', mode='before')
    def extraer_celular(cls, v: Any, info):
        if isinstance(v, str):
            return v
        return None

    class Config:
        from_attributes = True