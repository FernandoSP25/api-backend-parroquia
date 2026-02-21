from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.dependencies.database import get_db
from app.dependencies.auth import RoleChecker, get_current_active_user
from app.schemas.confirmante import ConfirmanteCreateFull, ConfirmanteOut
from app.services.confirmante_service import ConfirmanteService

router = APIRouter(prefix="/confirmantes", tags=["Confirmantes"])

# Permisos
allow_admin = RoleChecker(["ADMIN"])
allow_staff = RoleChecker(["ADMIN", "CATEQUISTA"])

@router.post("/", response_model=ConfirmanteOut, status_code=status.HTTP_201_CREATED)
def registrar_confirmante(
    data: ConfirmanteCreateFull, 
    db: Session = Depends(get_db),
    # current_user = Depends(allow_staff) # Descomentar para seguridad
):
    return ConfirmanteService.create(db, data)

@router.get("/", response_model=List[ConfirmanteOut])
def listar_confirmantes(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    # current_user = Depends(allow_staff)
):
    return ConfirmanteService.get_all(db, skip, limit)

@router.get("/{id}", response_model=ConfirmanteOut)
def obtener_confirmante(
    id: UUID, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    confirmante = ConfirmanteService.get_by_id(db, id)
    if not confirmante:
        raise HTTPException(status_code=404, detail="Confirmante no encontrado")
    return confirmante

@router.delete("/{id}", status_code=status.HTTP_200_OK)
def eliminar_confirmante(
    id: UUID, 
    db: Session = Depends(get_db),
    current_user = Depends(allow_admin) # Solo Admin borra
):
    return ConfirmanteService.delete(db, id)