from pydantic import BaseModel, EmailStr, Field
from datetime import date
from uuid import UUID

# LO QUE RECIBES (Entrada)
class AdminCreate(BaseModel):
    nombres: str
    apellidos: str
    dni: str = Field(..., min_length=8, max_length=15)
    fecha_nacimiento: date
    email_personal: EmailStr  # Crucial para recuperar cuenta
    celular: str              # Se guardará en 'telefonos'
    password: str             # Seguridad manual obligatoria

# LO QUE RESPONDES (Salida)
class AdminOut(BaseModel):
    id: UUID
    nombres: str
    apellidos: str
    email_institucional: str
    activo: bool

    class Config:
        from_attributes = True