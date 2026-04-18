from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.dependencies.database import get_db
from app.dependencies.auth import get_current_active_user, RoleChecker
from app.schemas.usuario import UsuarioCreate, UsuarioUpdate, UsuarioOut , PaginatedUsuarios
from app.services.usuario_service import UsuarioService 

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])

# Permisos
allow_admin = RoleChecker(["ADMIN"])

@router.get("/me", response_model=UsuarioOut)
def obtener_mi_perfil(
    current_user = Depends(get_current_active_user)
):
    """Obtiene los datos del usuario que inició sesión"""
    return current_user

@router.put("/me", response_model=UsuarioOut)
def actualizar_mi_perfil(
    usuario_update: UsuarioUpdate, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """El usuario actualiza sus propios datos (Nombres, teléfono, etc)"""
    return UsuarioService.update(db, current_user, usuario_update)

@router.put("/me/password", response_model=UsuarioOut)
def cambiar_mi_password(
    usuario_update: UsuarioUpdate, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Endpoint dedicado a cambiar la contraseña del usuario actual."""
    if not usuario_update.password:
        raise HTTPException(status_code=400, detail="La nueva contraseña es requerida")
    
    return UsuarioService.update(db, current_user, usuario_update)

@router.get("/", response_model=PaginatedUsuarios)
def get_users(
    page: int = 1,
    page_size: int = 10,
    db: Session = Depends(get_db)
):
    return UsuarioService.get_all(db, page, page_size)

@router.post("/", response_model=UsuarioOut, status_code=status.HTTP_201_CREATED)
def crear_usuario(
    usuario: UsuarioCreate, 
    db: Session = Depends(get_db),
    # Opcional: ¿Cualquiera puede registrarse o solo admin crea usuarios?
    # Si es registro público, quita la dependencia de current_user
):
    return UsuarioService.create(db, usuario)

@router.get("/{user_id}", response_model=UsuarioOut)
def obtener_usuario(
    user_id: UUID, 
    db: Session = Depends(get_db),
    #current_user = Depends(get_current_active_user)
):
    user = UsuarioService.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user

@router.put("/{user_id}", response_model=UsuarioOut)
def actualizar_usuario(
    user_id: UUID, 
    usuario_update: UsuarioUpdate, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    # Validar que el usuario se edite a sí mismo o sea Admin
    # (Lógica simplificada, asumiendo que el usuario existe)
    user = UsuarioService.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
    return UsuarioService.update(db, user, usuario_update)

@router.post("/{user_id}/desactivar", status_code=status.HTTP_200_OK)
def desactivar_usuario(
    user_id: UUID, 
    db: Session = Depends(get_db)
):
    # Aquí podrías pasar el ID del admin que ejecuta la acción si tienes autenticación
    return UsuarioService.desactivar(db, user_id)

@router.post("/{user_id}/reactivar", status_code=status.HTTP_200_OK)
def reactivar_usuario(
    user_id: UUID, 
    db: Session = Depends(get_db)
):
    return UsuarioService.reactivar(db, user_id)