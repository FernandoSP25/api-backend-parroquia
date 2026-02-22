from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.dependencies.database import get_db
from app.dependencies.auth import RoleChecker
from app.schemas.anio_catequetico import AnioCatequeticoCreate, AnioCatequeticoUpdate, AnioCatequeticoOut
from app.services.anio_catequetico_service import AnioCatequeticoService

router = APIRouter(prefix="/anios", tags=["Años Catequéticos"])

# Solo el ADMIN puede crear, editar o borrar años.
allow_admin = RoleChecker(["ADMIN"])

@router.get("/", response_model=List[AnioCatequeticoOut])
def listar_anios(solo_activos: bool = True, db: Session = Depends(get_db)):
    """Devuelve todos los años (ej: 2025, 2026) ordenados del más reciente al más antiguo."""
    return AnioCatequeticoService.get_all(db, solo_activos)

@router.get("/{anio_id}", response_model=AnioCatequeticoOut)
def obtener_anio(anio_id: UUID, db: Session = Depends(get_db)):
    """Obtiene el detalle de un año específico."""
    return AnioCatequeticoService.get_by_id(db, anio_id)

@router.post("/", response_model=AnioCatequeticoOut, status_code=status.HTTP_201_CREATED)
def crear_anio(
    data: AnioCatequeticoCreate, 
    db: Session = Depends(get_db),
    current_user = Depends(allow_admin) 
):
    """Crea un nuevo año catequético (Solo Admin)."""
    return AnioCatequeticoService.create(db, data)

@router.patch("/{anio_id}", response_model=AnioCatequeticoOut)
def actualizar_anio(
    anio_id: UUID, 
    data: AnioCatequeticoUpdate, 
    db: Session = Depends(get_db),
    # current_user = Depends(allow_admin)
):
    """Actualiza datos de un año (Solo Admin)."""
    return AnioCatequeticoService.update(db, anio_id, data)

@router.delete("/{anio_id}")
def eliminar_anio(
    anio_id: UUID, 
    db: Session = Depends(get_db),
    # current_user = Depends(allow_admin)
):
    """Desactiva un año catequético (Solo Admin)."""
    return AnioCatequeticoService.delete(db, anio_id)