from pydantic import BaseModel, Field, model_validator
from typing import Optional
from datetime import date, datetime
from uuid import UUID

class AnioCatequeticoBase(BaseModel):
    anio: int = Field(..., description="Año de la catequesis, ej: 2026")
    fecha_inicio: Optional[date] = None
    fecha_fin: Optional[date] = None
    descripcion: Optional[str] = None
    activo: bool = True

class AnioCatequeticoCreate(AnioCatequeticoBase):
    @model_validator(mode='after')
    def validar_fechas(self):
        # Protegemos que la lógica coincida con tu CONSTRAINT chk_fechas_anio de SQL
        if self.fecha_inicio and self.fecha_fin and self.fecha_fin < self.fecha_inicio:
            raise ValueError('La fecha de fin debe ser posterior a la fecha de inicio')
        return self

class AnioCatequeticoUpdate(BaseModel):
    anio: Optional[int] = None
    fecha_inicio: Optional[date] = None
    fecha_fin: Optional[date] = None
    descripcion: Optional[str] = None
    activo: Optional[bool] = None

class AnioCatequeticoOut(AnioCatequeticoBase):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True