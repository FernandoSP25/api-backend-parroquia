from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import date, datetime
from app.models.inscripcion import EstadoInscripcion

# --- BASE ---
class InscripcionBase(BaseModel):
    nombres: str
    apellidos: str
    dni: str = Field(min_length=8, max_length=8)
    fecha_nacimiento: date

    direccion: str
    email: Optional[EmailStr] = None
    celular_joven: str
    
    nombre_apoderado: str
    celular_apoderado: str

# --- CREATE (Lo que llega del Formulario Next.js) ---
class InscripcionCreate(InscripcionBase):
    pass 
    # No pedimos estado ni notas, eso es interno

# --- UPDATE (Para la secretaria) ---
class InscripcionUpdate(BaseModel):
    # Todo opcional para editar solo lo necesario
    nombres: Optional[str] = None
    apellidos: Optional[str] = None
    dni: Optional[str] = None
    estado: Optional[EstadoInscripcion] = None # Para aprobar/rechazar
    notas_internas: Optional[str] = None

# --- OUT (Respuesta al Frontend/Admin) ---
class InscripcionOut(InscripcionBase):
    id: int
    estado: EstadoInscripcion
    edad: int
    fecha_registro: datetime
    notas_internas: Optional[str] = None

    class Config:
        from_attributes = True