from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.dependencies.database import get_db
from app.dependencies.auth import RoleChecker
from app.schemas.telefono import TelefonoCreate, TelefonoUpdate, TelefonoOut
from app.services.telefono_service import TelefonoService

# Permisos: Admin y Catequista pueden gestionar teléfonos
allow_write = RoleChecker(["ADMIN", "CATEQUISTA"])

router = APIRouter(prefix="/telefonos", tags=["Teléfonos"])

@router.get("/usuario/{usuario_id}", response_model=List[TelefonoOut])
def listar_telefonos_usuario(
    usuario_id: UUID, 
    db: Session = Depends(get_db),
    current_user = Depends(allow_write)
):
    """Lista todos los teléfonos de un usuario"""
    return TelefonoService.get_by_usuario(db, usuario_id)

@router.post("/", response_model=TelefonoOut, status_code=status.HTTP_201_CREATED)
def agregar_telefono(
    data: TelefonoCreate, 
    db: Session = Depends(get_db),
    current_user = Depends(allow_write)
):
    """Agrega un nuevo teléfono a un usuario"""
    return TelefonoService.create(db, data)

@router.put("/{telefono_id}", response_model=TelefonoOut)
def actualizar_telefono(
    telefono_id: UUID,
    data: TelefonoUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(allow_write)
):
    """Actualiza un teléfono existente"""
    return TelefonoService.update(db, telefono_id, data)

@router.delete("/{telefono_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_telefono(
    telefono_id: UUID, 
    db: Session = Depends(get_db),
    current_user = Depends(allow_write)
):
    """Elimina un teléfono"""
    TelefonoService.delete(db, telefono_id)