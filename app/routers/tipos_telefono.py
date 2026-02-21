from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies.database import get_db
from app.schemas.tipo_telefono import (
    TipoTelefonoCreate,
    TipoTelefonoUpdate,
    TipoTelefonoOut
)
from app.services import tipo_telefono_service

router = APIRouter(prefix="/tipos-telefono", tags=["Tipos Teléfono"])

@router.get("/", response_model=list[TipoTelefonoOut])
def listar(db: Session = Depends(get_db)):
    return tipo_telefono_service.get_all(db)

@router.post("/", response_model=TipoTelefonoOut, status_code=status.HTTP_201_CREATED)
def crear(data: TipoTelefonoCreate, db: Session = Depends(get_db)):
    return tipo_telefono_service.create(db, data)

@router.put("/{tipo_id}", response_model=TipoTelefonoOut)
def actualizar(tipo_id: int, data: TipoTelefonoUpdate, db: Session = Depends(get_db)):
    obj = tipo_telefono_service.get_by_id(db, tipo_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Tipo de teléfono no encontrado")
    return tipo_telefono_service.update(db, obj, data)

@router.delete("/{tipo_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar(tipo_id: int, db: Session = Depends(get_db)):
    obj = tipo_telefono_service.get_by_id(db, tipo_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Tipo de teléfono no encontrado")
    tipo_telefono_service.delete(db, obj)
