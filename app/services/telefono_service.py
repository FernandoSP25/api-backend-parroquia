from sqlalchemy.orm import Session
from fastapi import HTTPException
from uuid import UUID
from app.models.telefono import Telefono
from app.schemas.telefono import TelefonoCreate, TelefonoUpdate

class TelefonoService:

    @staticmethod
    def get_by_usuario(db: Session, usuario_id: UUID):
        return db.query(Telefono).filter(Telefono.usuario_id == usuario_id).all()

    @staticmethod
    def create(db: Session, data: TelefonoCreate):
        # 1. Si este será el principal, desmarcar los otros del usuario
        if data.principal:
            db.query(Telefono).filter(
                Telefono.usuario_id == data.usuario_id,
                Telefono.principal == True
            ).update({"principal": False})
        
        # 2. Crear el nuevo
        nuevo_tel = Telefono(
            usuario_id=data.usuario_id,
            tipo_id=data.tipo_id,
            numero=data.numero,
            extension=data.extension,
            principal=data.principal
        )
        db.add(nuevo_tel)
        db.commit()
        db.refresh(nuevo_tel)
        return nuevo_tel

    @staticmethod
    def update(db: Session, telefono_id: UUID, data: TelefonoUpdate):
        telefono = db.query(Telefono).filter(Telefono.id == telefono_id).first()
        if not telefono:
            raise HTTPException(status_code=404, detail="Teléfono no encontrado")

        # Lógica de principal en actualización
        if data.principal is True:
            # Desmarcar otros teléfonos del mismo usuario
            db.query(Telefono).filter(
                Telefono.usuario_id == telefono.usuario_id,
                Telefono.id != telefono_id, # Todos menos este
                Telefono.principal == True
            ).update({"principal": False})

        # Actualizar campos
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(telefono, key, value)

        db.commit()
        db.refresh(telefono)
        return telefono

    @staticmethod
    def delete(db: Session, telefono_id: UUID):
        telefono = db.query(Telefono).filter(Telefono.id == telefono_id).first()
        if not telefono:
            raise HTTPException(status_code=404, detail="Teléfono no encontrado")
        
        db.delete(telefono)
        db.commit()