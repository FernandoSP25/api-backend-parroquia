from pydantic import BaseModel
from typing import Optional

class TipoTelefonoBase(BaseModel):
    codigo: str
    nombre: str
    activo: bool = True

class TipoTelefonoCreate(TipoTelefonoBase):
    pass

class TipoTelefonoUpdate(BaseModel):
    nombre: Optional[str] = None
    activo: Optional[bool] = None

class TipoTelefonoOut(TipoTelefonoBase):
    id: int

    class Config:
        from_attributes = True
