from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.dependencies.database import get_db
from app.dependencies.auth import get_current_active_user, RoleChecker
from app.schemas.rol import RolOut, RolCreate, RolAsignacionRequest, UsuarioRolOut
from app.services.rol_service import RolService

# Solo ADMIN puede gestionar roles
allow_admin = RoleChecker(["ADMIN"])

router = APIRouter(prefix="/roles", tags=["Roles y Permisos"])

# --- ENDPOINTS DE CATÁLOGO DE ROLES ---

@router.get("/", response_model=List[RolOut])
def listar_roles_disponibles(db: Session = Depends(get_db)):
    """Lista todos los roles disponibles en el sistema (ADMIN, CATEQUISTA, etc.)"""
    return RolService.get_all_roles(db)

@router.post("/", response_model=RolOut, status_code=status.HTTP_201_CREATED, dependencies=[Depends(allow_admin)])
def crear_nuevo_rol(data: RolCreate, db: Session = Depends(get_db)):
    """Crea un nuevo tipo de rol en el sistema"""
    # Validar si ya existe
    if RolService.get_by_name(db, data.nombre):
        raise HTTPException(status_code=400, detail="El rol ya existe")
    return RolService.create_rol(db, data)

# --- ENDPOINTS DE ASIGNACIÓN A USUARIOS ---

@router.post("/asignar", status_code=status.HTTP_200_OK)
def asignar_rol_usuario(
    data: RolAsignacionRequest, 
    db: Session = Depends(get_db),
    current_user = Depends(allow_admin) # Necesitamos el usuario actual para el campo 'asignado_por'
):
    """Asigna un rol a un usuario específico"""
    RolService.asignar_rol(db, data, admin_id=current_user.id)
    return {"message": "Rol asignado correctamente"}

@router.get("/usuario/{usuario_id}", response_model=List[UsuarioRolOut], dependencies=[Depends(allow_admin)])
def obtener_roles_usuario(usuario_id: UUID, db: Session = Depends(get_db)):
    """Devuelve la lista de roles activos de un usuario"""
    return RolService.get_user_roles(db, usuario_id)

@router.delete("/revocar/{usuario_id}/{rol_id}", dependencies=[Depends(allow_admin)])
def revocar_rol_usuario(usuario_id: UUID, rol_id: UUID, db: Session = Depends(get_db)):
    """Quita (desactiva) un rol a un usuario"""
    return RolService.revocar_rol(db, usuario_id, rol_id)