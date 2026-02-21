from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from datetime import date
from uuid import UUID
from dateutil.relativedelta import relativedelta

# --- BASE COMÚN (Lectura/Updates parciales) ---
class ConfirmanteBase(BaseModel):
    # Familia
    apoderado_nombre: Optional[str] = None
    apoderado_telefono: Optional[str] = None
    apoderado_email: Optional[EmailStr] = None
    apoderado_relacion: Optional[str] = "PADRE"

    # Padrinos
    nombre_padrino: Optional[str] = None
    telefono_padrino: Optional[str] = None
    email_padrino: Optional[EmailStr] = None

    # Sacramentos
    bautizado: bool = True
    parroquia_bautismo: Optional[str] = None
    fecha_bautismo: Optional[date] = None
    libro_bautismo: Optional[str] = None
    folio_bautismo: Optional[str] = None

# --- INPUT: CREACIÓN (Reglas Estrictas) ---
class ConfirmanteCreateFull(ConfirmanteBase):
    # DATOS DE USUARIO
    nombres: str = Field(..., min_length=2)
    apellidos: str = Field(..., min_length=2)
    dni: str = Field(..., min_length=8, max_length=15)
    fecha_nacimiento: date
    email_personal: EmailStr = Field(..., description="Email personal obligatorio (ej: gmail)")
    celular: str = Field(..., min_length=9, description="Celular del joven obligatorio")
    
    celular: str = Field(..., min_length=9)
    foto_url: Optional[str] = None

    # VALIDACIÓN DE EDAD
    @field_validator('fecha_nacimiento')
    def validar_edad(cls, v):
        edad = relativedelta(date.today(), v).years
        if edad < 12:
            raise ValueError('El confirmante debe tener al menos 12 años.')
        return v

# --- OUTPUT: RESPUESTA ---
class UsuarioResumen(BaseModel):
    id: UUID
    nombres: str
    apellidos: str
    email: EmailStr     # Email Institucional generado
    email_personal: Optional[EmailStr] # Email Personal
    dni: str
    activo: bool
    foto_url: Optional[str] = None

class ConfirmanteOut(ConfirmanteBase):
    id: UUID
    usuario_id: UUID
    fecha_inscripcion: date
    activo: bool
    
    # Datos del usuario anidados
    usuario: Optional[UsuarioResumen] = None 
    celular: Optional[str] = None

    
    class Config:
        from_attributes = True