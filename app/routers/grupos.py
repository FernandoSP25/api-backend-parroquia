from fastapi import APIRouter, Depends, Body
from sqlalchemy.orm import Session
from uuid import UUID
from typing import Optional

from app.dependencies.database import get_db
from app.schemas.grupo_kanban import TableroGrupos
from app.services.grupo_service import GrupoService

router = APIRouter(prefix="/grupos", tags=["Gestión de Grupos"])

@router.get("/tablero/{anio_id}", response_model=TableroGrupos)
def ver_tablero_kanban(anio_id: UUID, db: Session = Depends(get_db)):
    """Obtiene toda la estructura para el Drag & Drop"""
    return GrupoService.obtener_tablero(db, anio_id)

@router.patch("/mover-confirmante")
def mover_confirmante(
    confirmante_id: UUID = Body(...),
    grupo_id: Optional[UUID] = Body(None), # Null = Enviar a 'Sin Asignar'
    db: Session = Depends(get_db)
):
    """API que llama el Frontend al soltar la tarjeta"""
    return GrupoService.mover_confirmante(db, confirmante_id, grupo_id)

@router.patch("/mover-catequista")
def mover_catequista(
    catequista_id: UUID = Body(...),
    grupo_id: Optional[UUID] = Body(None),
    db: Session = Depends(get_db)
):
    return GrupoService.mover_catequista(db, catequista_id, grupo_id)