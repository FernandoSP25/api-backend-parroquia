from sqlalchemy.orm import Session
from app.models.tipo_qr import TipoQr
from app.schemas.tipo_qr import TipoQRCreate, TipoQRUpdate

def get_all(db: Session):
    return db.query(TipoQr).all()

def get_by_id(db: Session, tipo_qr_id: int):
    return db.query(TipoQr).filter(TipoQr.id == tipo_qr_id).first()

def create(db: Session, data: TipoQRCreate):
    obj = TipoQr(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

def update(db: Session, obj: TipoQr, data: TipoQRUpdate):
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(obj, field, value)
    db.commit()
    db.refresh(obj)
    return obj

def delete(db: Session, obj: TipoQr):
    obj.activo = False
    db.commit()
