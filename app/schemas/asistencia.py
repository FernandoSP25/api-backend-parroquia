from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional

# Lo que recibimos del escáner en Next.js
class AsistenciaQRRequest(BaseModel):
    codigo_leido: str

# Lo que le devolvemos como respuesta al celular
class AsistenciaResponse(BaseModel):
    id: UUID
    evento_id: UUID
    fecha: datetime
    metodo: str
    mensaje: str = "Asistencia registrada correctamente"

    class Config:
        from_attributes = True