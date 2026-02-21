from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class TipoEventoBase(BaseModel):
    codigo: str
    nombre: str
    descripcion: Optional[str] = None
    icono: Optional[str] = None
    color: Optional[str] = None
    requiere_asistencia: bool = True
    orden: Optional[int] = None
    activo: bool = True


class TipoEventoCreate(TipoEventoBase):
    pass


class TipoEventoUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    icono: Optional[str] = None
    color: Optional[str] = None
    requiere_asistencia: Optional[bool] = None
    orden: Optional[int] = None
    activo: Optional[bool] = None


class TipoEventoOut(TipoEventoBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
