from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, time, datetime
from uuid import UUID

class EventoBase(BaseModel):
    nombre: str = Field(..., max_length=150)
    tipo_id: Optional[int] = None
    descripcion: Optional[str] = None
    obligatorio: bool = False
    fecha: date
    hora_inicio: Optional[time] = None
    hora_fin: Optional[time] = None
    ubicacion: Optional[str] = Field(None, max_length=200)
    grupo_id: Optional[UUID] = None
    max_asistentes: Optional[int] = None
    requiere_confirmacion: bool = False
    latitud: Optional[float] = None  
    longitud: Optional[float] = None

class EventoCreate(EventoBase):
    pass # El 'creado_por' lo sacaremos del token del usuario logueado en el futuro

class EventoUpdate(BaseModel):
    nombre: Optional[str] = Field(None, max_length=150)
    tipo_id: Optional[int] = None
    descripcion: Optional[str] = None
    obligatorio: Optional[bool] = None
    fecha: Optional[date] = None
    hora_inicio: Optional[time] = None
    hora_fin: Optional[time] = None
    ubicacion: Optional[str] = Field(None, max_length=200)
    max_asistentes: Optional[int] = None
    requiere_confirmacion: Optional[bool] = None
    activo: Optional[bool] = None

class EventoResponse(EventoBase):
    id: UUID
    creado_por: Optional[UUID]
    activo: bool
    created_at: datetime

    class Config:
        from_attributes = True