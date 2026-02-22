from sqlalchemy.orm import Session
from fastapi import HTTPException
from uuid import UUID
from app.models.anio_catequetico import AnioCatequetico
from app.schemas.anio_catequetico import AnioCatequeticoCreate, AnioCatequeticoUpdate

class AnioCatequeticoService:
    @staticmethod
    def get_all(db: Session, solo_activos: bool = True):
        query = db.query(AnioCatequetico)
        if solo_activos:
            query = query.filter(AnioCatequetico.activo == True)
        # Ordenamos descendente para que el año actual (ej. 2026) salga primero
        return query.order_by(AnioCatequetico.anio.desc()).all()

    @staticmethod
    def get_by_id(db: Session, anio_id: UUID):
        anio = db.query(AnioCatequetico).filter(AnioCatequetico.id == anio_id).first()
        if not anio:
            raise HTTPException(status_code=404, detail="Año catequético no encontrado")
        return anio

    @staticmethod
    def create(db: Session, data: AnioCatequeticoCreate):
        # Validar duplicados (UNIQUE en SQL)
        if db.query(AnioCatequetico).filter(AnioCatequetico.anio == data.anio).first():
            raise HTTPException(status_code=400, detail=f"El año {data.anio} ya existe en el sistema.")
        
        nuevo_anio = AnioCatequetico(**data.model_dump())
        db.add(nuevo_anio)
        db.commit()
        db.refresh(nuevo_anio)
        return nuevo_anio

    @staticmethod
    def update(db: Session, anio_id: UUID, data: AnioCatequeticoUpdate):
        anio_db = AnioCatequeticoService.get_by_id(db, anio_id)
        
        update_data = data.model_dump(exclude_unset=True)
        
        # Validar duplicado si intenta cambiar el año por uno que ya existe
        if 'anio' in update_data and update_data['anio'] != anio_db.anio:
            if db.query(AnioCatequetico).filter(AnioCatequetico.anio == update_data['anio']).first():
                raise HTTPException(status_code=400, detail="Ese año ya está registrado.")
                
        for key, value in update_data.items():
            setattr(anio_db, key, value)
            
        # Validar fechas después de actualizar
        if anio_db.fecha_inicio and anio_db.fecha_fin and anio_db.fecha_fin < anio_db.fecha_inicio:
            raise HTTPException(status_code=400, detail="La fecha fin debe ser mayor a la fecha de inicio.")

        db.commit()
        db.refresh(anio_db)
        return anio_db

    @staticmethod
    def delete(db: Session, anio_id: UUID):
        anio_db = AnioCatequeticoService.get_by_id(db, anio_id)
        anio_db.activo = False # Soft delete
        db.commit()
        return {"message": "Año desactivado correctamente"}