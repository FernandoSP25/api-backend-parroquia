from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class TipoEventoBase(BaseModel):
    codigo: str
    nombre: str
    icono: Optional[str] = None
    color: Optional[str] = None

# Lo que usaremos para el Selector en el Frontend
class TipoEventoOut(TipoEventoBase):
    id: int

    class Config:
        from_attributes = True

# Schemas de creación y actualización se mantienen igual
class TipoEventoCreate(TipoEventoBase):
    descripcion: Optional[str] = None
    requiere_asistencia: bool = True
    orden: Optional[int] = None

class TipoEventoUpdate(BaseModel):
    nombre: Optional[str] = None
    icono: Optional[str] = None
    color: Optional[str] = None
    activo: Optional[bool] = None