from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID

# --- TARJETA DE CONFIRMANTE ---
class ConfirmanteCard(BaseModel):
    id: UUID          # ID del Confirmante (no del usuario)
    nombres: str      # Viene del usuario
    apellidos: str    # Viene del usuario
    edad: int         # Calculado para saber si encaja en el grupo
    foto_url: Optional[str] = None

# --- CABECERA DE CATEQUISTA ---
class CatequistaBadge(BaseModel):
    id: UUID          # ID del Catequista
    nombres: str
    apellidos: str
    foto_url: Optional[str] = None
    es_principal: bool = False # Si definieras un líder

# --- COLUMNA DE GRUPO ---
class GrupoColumna(BaseModel):
    id: UUID
    nombre: str
    capacidad_maxima: int
    total_inscritos: int
    
    # Listas dentro de la columna
    catequistas: List[CatequistaBadge] = []
    confirmantes: List[ConfirmanteCard] = []

# --- RESPUESTA FINAL DEL TABLERO ---
class TableroGrupos(BaseModel):
    sin_asignar_confirmantes: List[ConfirmanteCard] # ✅ Nueva
    sin_asignar_catequistas: List[CatequistaBadge]  # ✅ Nueva

    grupos: List[GrupoColumna]