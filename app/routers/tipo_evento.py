from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies.database import get_db
from app.schemas.tipo_evento import (
    TipoEventoCreate,
    TipoEventoUpdate,
    TipoEventoOut,
)
from app.services import tipo_evento_service as service

router = APIRouter(prefix="/tipos-evento", tags=["Tipos de Evento"])


@router.post("/", response_model=TipoEventoOut, status_code=status.HTTP_201_CREATED)
def crear_tipo_evento(data: TipoEventoCreate, db: Session = Depends(get_db)):
    return service.crear(db, data)


@router.get("/", response_model=list[TipoEventoOut])
def listar_tipos_evento(db: Session = Depends(get_db)):
    return service.listar(db)


@router.get("/{tipo_evento_id}", response_model=TipoEventoOut)
def obtener_tipo_evento(tipo_evento_id: int, db: Session = Depends(get_db)):
    obj = service.obtener(db, tipo_evento_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Tipo de evento no encontrado")
    return obj


@router.put("/{tipo_evento_id}", response_model=TipoEventoOut)
def actualizar_tipo_evento(
    tipo_evento_id: int,
    data: TipoEventoUpdate,
    db: Session = Depends(get_db),
):
    obj = service.obtener(db, tipo_evento_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Tipo de evento no encontrado")

    return service.actualizar(db, obj, data)


@router.delete("/{tipo_evento_id}", response_model=TipoEventoOut)
def eliminar_tipo_evento(tipo_evento_id: int, db: Session = Depends(get_db)):
    obj = service.obtener(db, tipo_evento_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Tipo de evento no encontrado")

    return service.eliminar(db, obj)
