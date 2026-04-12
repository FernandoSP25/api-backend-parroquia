from pydantic import BaseModel
from typing import List, Optional
from datetime import date, time
from uuid import UUID

class DashboardKPIs(BaseModel):
    total_confirmantes: int
    total_catequistas: int
    total_grupos: int
    asistencia_promedio: float

class EventoResumen(BaseModel):
    id: UUID
    nombre: str
    fecha: date
    hora_inicio: Optional[time] = None
    ubicacion: Optional[str] = None
    tipo_nombre: str
    icono: str

class DashboardResponse(BaseModel):
    kpis: DashboardKPIs
    proximos_eventos: List[EventoResumen]
    
    
class DashboardCatequistaKPIs(BaseModel):
    grupo_nombre: str
    total_jovenes: int
    asistencia_promedio: float
    jovenes_en_riesgo: int

class DashboardCatequistaResponse(BaseModel):
    kpis: DashboardCatequistaKPIs
    proximos_eventos: List[EventoResumen]