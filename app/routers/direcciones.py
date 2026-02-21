from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from typing import Optional

from app.dependencies.database import get_db
from app.dependencies.auth import get_current_active_user, RoleChecker
from app.schemas.direccion import DireccionCreate, DireccionUpdate, DireccionOut
from app.services.direccion_service import DireccionService

# Permitimos que ADMIN y CATEQUISTA (quizás para sus alumnos) gestionen
# OJO: Si quieres que el propio usuario edite su dirección, la lógica de permisos sería distinta.
# Por ahora lo dejo para ADMIN/CATEQUISTA.
allow_write = RoleChecker(["ADMIN", "CATEQUISTA"])

router = APIRouter(prefix="/direcciones", tags=["Direcciones"])

@router.get("/usuario/{usuario_id}", response_model=Optional[DireccionOut])
def obtener_direccion_usuario(
    usuario_id: UUID, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user) # Cualquier usuario logueado puede intentar ver (validar permisos si es necesario)
):
    """Obtiene la dirección de un usuario específico"""
    direccion = DireccionService.get_by_usuario_id(db, usuario_id)
    if not direccion:
        raise HTTPException(status_code=404, detail="Dirección no encontrada")
    return direccion

@router.post("/", response_model=DireccionOut, status_code=status.HTTP_201_CREATED)
def crear_direccion(
    data: DireccionCreate, 
    db: Session = Depends(get_db),
    current_user = Depends(allow_write)
):
    """Registra una dirección nueva para un usuario"""
    return DireccionService.create(db, data)

@router.put("/usuario/{usuario_id}", response_model=DireccionOut)
def actualizar_direccion(
    usuario_id: UUID,
    data: DireccionUpdate, 
    db: Session = Depends(get_db),
    current_user = Depends(allow_write)
):
    """Actualiza la dirección existente de un usuario"""
    return DireccionService.update_by_usuario(db, usuario_id, data)