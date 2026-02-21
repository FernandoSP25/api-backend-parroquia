from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.dependencies.database import get_db
from app.dependencies.auth import RoleChecker
from app.schemas.usuario_rol import UsuarioRolCreate, UsuarioRolOut
from app.services.usuario_rol_service import UsuarioRolService

# Solo ADMIN puede tocar esta tabla directamente
allow_admin = RoleChecker(["ADMIN"])

router = APIRouter(prefix="/usuario-roles", tags=["Usuario Roles (Asignaciones)"])

@router.post("/", response_model=UsuarioRolOut, status_code=status.HTTP_201_CREATED)
def asignar_rol(
    data: UsuarioRolCreate, 
    db: Session = Depends(get_db),
    current_user = Depends(allow_admin) # Necesitamos el usuario actual para 'asignado_por'
):
    """Asigna manualmente un rol a un usuario (crea registro en usuario_roles)"""
    return UsuarioRolService.create(db, data, admin_id=current_user.id)

@router.get("/usuario/{usuario_id}", response_model=List[UsuarioRolOut])
def ver_roles_de_usuario(
    usuario_id: UUID, 
    db: Session = Depends(get_db),
    current_user = Depends(allow_admin)
):
    """Obtiene todas las filas de usuario_roles para un usuario específico"""
    return UsuarioRolService.get_by_usuario_id(db, usuario_id)

@router.delete("/{usuario_id}/{rol_id}", status_code=status.HTTP_204_NO_CONTENT)
def quitar_rol(
    usuario_id: UUID, 
    rol_id: UUID, 
    db: Session = Depends(get_db),
    current_user = Depends(allow_admin)
):
    """Desactiva un rol de un usuario (Soft Delete)"""
    UsuarioRolService.soft_delete(db, usuario_id, rol_id)