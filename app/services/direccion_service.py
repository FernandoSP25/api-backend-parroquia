from sqlalchemy.orm import Session
from fastapi import HTTPException
from uuid import UUID
from app.models.direccion import Direccion
from app.schemas.direccion import DireccionCreate, DireccionUpdate

class DireccionService:

    @staticmethod
    def get_by_usuario_id(db: Session, usuario_id: UUID):
        return db.query(Direccion).filter(Direccion.usuario_id == usuario_id).first()

    @staticmethod
    def create(db: Session, data: DireccionCreate):
        # 1. Verificar si el usuario ya tiene dirección
        existing = db.query(Direccion).filter(Direccion.usuario_id == data.usuario_id).first()
        if existing:
            raise HTTPException(status_code=400, detail="El usuario ya tiene una dirección registrada. Usa actualizar.")

        # 2. Crear nueva
        nueva_dir = Direccion(
            usuario_id=data.usuario_id,
            direccion=data.direccion,
            referencia=data.referencia,
            distrito=data.distrito,
            provincia=data.provincia,
            departamento=data.departamento,
            codigo_postal=data.codigo_postal
        )
        db.add(nueva_dir)
        db.commit()
        db.refresh(nueva_dir)
        return nueva_dir

    @staticmethod
    def update_by_usuario(db: Session, usuario_id: UUID, data: DireccionUpdate):
        direccion = db.query(Direccion).filter(Direccion.usuario_id == usuario_id).first()
        if not direccion:
            raise HTTPException(status_code=404, detail="Dirección no encontrada para este usuario")

        # Actualizar campos dinámicamente
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(direccion, key, value)

        db.commit()
        db.refresh(direccion)
        return direccion

    @staticmethod
    def delete(db: Session, usuario_id: UUID):
        direccion = db.query(Direccion).filter(Direccion.usuario_id == usuario_id).first()
        if not direccion:
            raise HTTPException(status_code=404, detail="Dirección no encontrada")
        
        db.delete(direccion)
        db.commit()