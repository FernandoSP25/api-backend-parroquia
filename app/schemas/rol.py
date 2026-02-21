from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from datetime import datetime

# --- SCHEMAS DE ROL (Catálogo) ---

class RolBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    activo: bool = True

class RolCreate(RolBase):
    pass # Se usa para crear nuevos roles si fuera necesario

class RolOut(RolBase):
    id: UUID
    
    class Config:
        from_attributes = True

# --- SCHEMAS DE ASIGNACIÓN (Usuario <-> Rol) ---

# Lo que recibes para asignar un rol
class RolAsignacionRequest(BaseModel):
    usuario_id: UUID
    rol_id: UUID

# Lo que respondes cuando listas los roles de un usuario
class UsuarioRolOut(BaseModel):
    id: UUID
    rol_id: UUID
    rol_nombre: str       # ¡Importante! Para que el frontend muestre "ADMIN" y no un UUID raro
    rol_descripcion: Optional[str]
    asignado_en: datetime
    activo: bool

    class Config:
        from_attributes = True