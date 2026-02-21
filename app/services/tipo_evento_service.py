from sqlalchemy.orm import Session
from app.models.tipo_evento import TipoEvento
from app.schemas.tipo_evento import TipoEventoCreate, TipoEventoUpdate


def crear(db: Session, data: TipoEventoCreate):
    obj = TipoEvento(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def listar(db: Session):
    return (
        db.query(TipoEvento)
        .filter(TipoEvento.activo == True)
        .order_by(TipoEvento.orden)
        .all()
    )


def obtener(db: Session, tipo_evento_id: int):
    return (
        db.query(TipoEvento)
        .filter(TipoEvento.id == tipo_evento_id, TipoEvento.activo == True)
        .first()
    )


def actualizar(db: Session, obj: TipoEvento, data: TipoEventoUpdate):
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(obj, field, value)

    db.commit()
    db.refresh(obj)
    return obj


def eliminar(db: Session, obj: TipoEvento):
    obj.activo = False
    db.commit()
    return obj
