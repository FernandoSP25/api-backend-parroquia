from sqlalchemy.orm import Session
from app.models.tipo_telefono import TipoTelefono
from app.schemas.tipo_telefono import TipoTelefonoCreate, TipoTelefonoUpdate

def get_all(db: Session):
    return db.query(TipoTelefono).all()

def get_by_id(db: Session, tipo_id: int):
    return db.query(TipoTelefono).filter(TipoTelefono.id == tipo_id).first()

def create(db: Session, data: TipoTelefonoCreate):
    obj = TipoTelefono(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

def update(db: Session, obj: TipoTelefono, data: TipoTelefonoUpdate):
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(obj, field, value)
    db.commit()
    db.refresh(obj)
    return obj

def delete(db: Session, obj: TipoTelefono):
    obj.activo = False
    db.commit()
