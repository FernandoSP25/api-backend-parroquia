from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional

# LO QUE RECIBES PARA CREAR (Input)
class UsuarioRolCreate(BaseModel):
    usuario_id: UUID
    rol_id: UUID

# LO QUE DEVUELVES (Output)
class UsuarioRolOut(BaseModel):
    id: UUID
    usuario_id: UUID
    rol_id: UUID
    asignado_por: Optional[UUID] = None
    asignado_en: datetime
    activo: bool

    class Config:
        from_attributes = True