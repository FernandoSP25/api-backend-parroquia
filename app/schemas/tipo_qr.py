from pydantic import BaseModel
from typing import Optional

class TipoQRBase(BaseModel):
    codigo: str
    nombre: str
    descripcion: Optional[str] = None
    activo: bool = True

class TipoQRCreate(TipoQRBase):
    pass

class TipoQRUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    activo: Optional[bool] = None

class TipoQROut(TipoQRBase):
    id: int

    class Config:
        from_attributes = True
