from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional, List

# Schema del Catálogo de Estados
class EstadoAsistenciaSchema(BaseModel):
    id: int
    codigo: str
    nombre: str
    color: Optional[str] = None

    class Config:
        from_attributes = True

# Lo que envía el Catequista por cada alumno
class AsistenciaUpdate(BaseModel):
    usuario_id: UUID
    estado_id: int
    observaciones: Optional[str] = None

# Para enviar toda el aula de un solo golpe (Checklist)
class AsistenciaBulkRequest(BaseModel):
    asistencias: List[AsistenciaUpdate]

# Lo que devolvemos al Frontend
class AsistenciaResponse(BaseModel):
    id: UUID
    usuario_id: UUID
    evento_id: UUID
    estado_id: int
    fecha: datetime
    observaciones: Optional[str] = None
    estado: Optional[EstadoAsistenciaSchema] = None

    class Config:
        from_attributes = True
        
class AlumnoChecklist(BaseModel):
    confirmante_id: UUID
    usuario_id: UUID      # El ID que usaremos para guardar la asistencia
    nombres: str
    apellidos: str
    foto_url: Optional[str] = None
    grupo_nombre: Optional[str] = None
    estado_id: int        # Por defecto vendrá 3 (Falta) si el catequista aún no guarda nada
    observaciones: Optional[str] = None

    class Config:
        from_attributes = True