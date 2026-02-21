from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies.database import get_db
from app.schemas.tipo_qr import TipoQRCreate, TipoQRUpdate, TipoQROut
from app.services import tipo_qr_service

router = APIRouter(prefix="/tipos-qr", tags=["Tipos QR"])

@router.get("/", response_model=list[TipoQROut])
def listar(db: Session = Depends(get_db)):
    return tipo_qr_service.get_all(db)

@router.post("/", response_model=TipoQROut, status_code=status.HTTP_201_CREATED)
def crear(data: TipoQRCreate, db: Session = Depends(get_db)):
    return tipo_qr_service.create(db, data)

@router.put("/{tipo_qr_id}", response_model=TipoQROut)
def actualizar(tipo_qr_id: int, data: TipoQRUpdate, db: Session = Depends(get_db)):
    obj = tipo_qr_service.get_by_id(db, tipo_qr_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Tipo QR no encontrado")
    return tipo_qr_service.update(db, obj, data)

@router.delete("/{tipo_qr_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar(tipo_qr_id: int, db: Session = Depends(get_db)):
    obj = tipo_qr_service.get_by_id(db, tipo_qr_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Tipo QR no encontrado")
    tipo_qr_service.delete(db, obj)
