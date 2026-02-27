from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from app.dependencies.database import get_db
# 1. Importamos tus dependencias de seguridad reales
from app.dependencies.auth import get_current_active_user, RoleChecker
from app.models.usuario import Usuario 
from app.schemas.evento import EventoCreate, EventoUpdate, EventoResponse
from app.services.evento_service import EventoService

router = APIRouter(prefix="/eventos", tags=["Gestión de Eventos"])

# 2. Definimos quién puede modificar o crear eventos (Seguridad)
permitir_modificacion = RoleChecker(["ADMIN", "CATEQUISTA"])

@router.get("/", response_model=List[EventoResponse])
def listar_eventos(
    grupo_id: Optional[UUID] = Query(None, description="Filtrar por Grupo"),
    solo_futuros: bool = Query(False, description="Mostrar solo eventos desde hoy en adelante"),
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    # Protegemos la ruta: cualquier usuario logueado (incluido Confirmante) puede ver eventos
    current_user: Usuario = Depends(get_current_active_user) 
):
    return EventoService.get_all(db, grupo_id, solo_futuros, skip, limit)

@router.get("/{evento_id}", response_model=EventoResponse)
def obtener_evento(
    evento_id: UUID, 
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    return EventoService.get_by_id(db, evento_id)

@router.post("/", response_model=EventoResponse)
def crear_evento(
    evento: EventoCreate, 
    db: Session = Depends(get_db),
    # 3. Exigimos que sea Admin o Catequista. FastAPI nos entrega el usuario real del Token.
    current_user: Usuario = Depends(permitir_modificacion) 
):
    # Pasamos el ID real de la base de datos (current_user.id) al servicio
    return EventoService.create(db, evento, current_user.id)

@router.patch("/{evento_id}", response_model=EventoResponse)
def actualizar_evento(
    evento_id: UUID, 
    evento: EventoUpdate, 
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(permitir_modificacion)
):
    return EventoService.update(db, evento_id, evento)

@router.delete("/{evento_id}")
def eliminar_evento(
    evento_id: UUID, 
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(permitir_modificacion)
):
    return EventoService.desactivar(db, evento_id)