# app/schemas/qr.py
from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime

class QrRequest(BaseModel):
    evento_id: UUID
    rol_generador: str  # Puede ser 'ADMIN' o 'CATEQUISTA'

class QrResponse(BaseModel):
    token_completo: str # Este es el string final que dibujará el QR (ej: "SJMV-uuid-token")
    expires_at: datetime
    
    class Config:
        from_attributes = True