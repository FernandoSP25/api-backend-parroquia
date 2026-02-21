from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID

# --- BASE ---
class GrupoBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    capacidad_maxima: int = 30

# --- CREATE ---
class GrupoCreate(GrupoBase):
    anio_id: UUID 

# --- UPDATE ---
class GrupoUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    capacidad_maxima: Optional[int] = None
    activo: Optional[bool] = None
