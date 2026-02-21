from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.dependencies.database import get_db
# 1. CORRECCIÓN: Importamos RoleChecker, NO allow_admin
from app.dependencies.auth import RoleChecker 
from app.schemas.inscripcion import InscripcionCreate, InscripcionOut, InscripcionUpdate
from app.services.inscripcion_service import InscripcionService

router = APIRouter(prefix="/inscripciones", tags=["Inscripciones"])

# 2. DEFINIMOS LA VARIABLE AQUÍ (Igual que en usuarios.py)
allow_admin = RoleChecker(["ADMIN"])

# --- ENDPOINT PÚBLICO (Formulario Web) ---
@router.post("/", response_model=InscripcionOut, status_code=status.HTTP_201_CREATED)
def registrar_inscripcion(
    inscripcion: InscripcionCreate, 
    db: Session = Depends(get_db)
):
    return InscripcionService.create(db, inscripcion)

# --- ENDPOINTS PROTEGIDOS (Panel Administrativo) ---

@router.get("/", response_model=List[InscripcionOut])
def listar_inscripciones(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    # Ahora sí funciona porque allow_admin está definido arriba 👆
    #current_user = Depends(allow_admin) 
):
    return InscripcionService.get_all(db, skip, limit)

@router.get("/{id}", response_model=InscripcionOut)
def obtener_inscripcion(
    id: int, 
    db: Session = Depends(get_db),
    current_user = Depends(allow_admin)
):
    inscripcion = InscripcionService.get_by_id(db, id)
    if not inscripcion:
        raise HTTPException(status_code=404, detail="Inscripción no encontrada")
    return inscripcion

@router.put("/{id}", response_model=InscripcionOut)
def actualizar_estado_o_notas(
    id: int, 
    data: InscripcionUpdate, 
    db: Session = Depends(get_db),
    current_user = Depends(allow_admin)
):
    return InscripcionService.update(db, id, data)