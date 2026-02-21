from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime

class TelefonoBase(BaseModel):
    numero: str = Field(..., min_length=7, max_length=15, description="Número de teléfono")
    extension: Optional[str] = None
    tipo_id: int
    principal: bool = False

# Input para crear
class TelefonoCreate(TelefonoBase):
    usuario_id: UUID

# Input para actualizar
class TelefonoUpdate(BaseModel):
    numero: Optional[str] = None
    extension: Optional[str] = None
    tipo_id: Optional[int] = None
    principal: Optional[bool] = None

# Output
class TelefonoOut(TelefonoBase):
    id: UUID
    usuario_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True