from pydantic import BaseModel, EmailStr, Field
from datetime import date
from uuid import UUID

# LO QUE RECIBES (Entrada)
class CatequistaCreate(BaseModel):
    nombres: str
    apellidos: str
    dni: str = Field(..., min_length=8, max_length=15)
    fecha_nacimiento: date
    email_personal: EmailStr  # Para contacto
    celular: str              # Se guardará en tabla 'telefonos'
    password: str             # Seguridad manual

# LO QUE RESPONDES (Salida)
class CatequistaOut(BaseModel):
    id: UUID
    usuario_id: UUID
    nombres: str
    apellidos: str
    email_institucional: str # El que generamos (nombre.apellido)
    activo: bool

    class Config:
        from_attributes = True