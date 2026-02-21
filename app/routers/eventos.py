from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from app.dependencies.database import get_db
from app.schemas.evento import EventoCreate, EventoUpdate, EventoResponse
from app.services.evento_service import EventoService

router = APIRouter(prefix="/eventos", tags=["Gestión de Eventos"])

# Mock de usuario logueado (Hasta que implementes la dependencia JWT real)
# TODO: Reemplazar esto con la dependencia get_current_user real
def get_current_user_id():
    # Retorna un UUID falso por ahora para probar, o pon un UUID de tu BD
    return UUID("51247507-af21-4537-a318-af3a823f15d4") 

@router.get("/", response_model=List[EventoResponse])
def listar_eventos(
    grupo_id: Optional[UUID] = Query(None, description="Filtrar por Grupo"),
    solo_futuros: bool = Query(False, description="Mostrar solo eventos desde hoy en adelante"),
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    return EventoService.get_all(db, grupo_id, solo_futuros, skip, limit)

@router.get("/{evento_id}", response_model=EventoResponse)
def obtener_evento(evento_id: UUID, db: Session = Depends(get_db)):
    return EventoService.get_by_id(db, evento_id)

@router.post("/", response_model=EventoResponse)
def crear_evento(
    evento: EventoCreate, 
    db: Session = Depends(get_db),
    usuario_id: UUID = Depends(get_current_user_id) # Se auto-llena con el usuario logueado
):
    return EventoService.create(db, evento, usuario_id)

@router.patch("/{evento_id}", response_model=EventoResponse)
def actualizar_evento(evento_id: UUID, evento: EventoUpdate, db: Session = Depends(get_db)):
    return EventoService.update(db, evento_id, evento)

@router.delete("/{evento_id}")
def eliminar_evento(evento_id: UUID, db: Session = Depends(get_db)):
    return EventoService.desactivar(db, evento_id)