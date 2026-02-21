from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime

class DireccionBase(BaseModel):
    direccion: str
    referencia: Optional[str] = None
    distrito: Optional[str] = None
    provincia: Optional[str] = None
    departamento: Optional[str] = None
    codigo_postal: Optional[str] = None

# Para crear (Input)
class DireccionCreate(DireccionBase):
    usuario_id: UUID

# Para actualizar (Input) - Todo opcional
class DireccionUpdate(BaseModel):
    direccion: Optional[str] = None
    referencia: Optional[str] = None
    distrito: Optional[str] = None
    provincia: Optional[str] = None
    departamento: Optional[str] = None
    codigo_postal: Optional[str] = None

# Para leer (Output)
class DireccionOut(DireccionBase):
    id: UUID
    usuario_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True