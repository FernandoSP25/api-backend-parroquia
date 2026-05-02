from sqlalchemy.orm import Session
from sqlalchemy import or_  
from fastapi import HTTPException
from uuid import UUID
from datetime import datetime, date
from app.models.evento import Evento
from app.schemas.evento import EventoCreate, EventoUpdate
from app.models.anio_catequetico import AnioCatequetico

class EventoService:

    @staticmethod
    def get_all(db: Session, anio_id: UUID = None, grupo_id: UUID = None, tipo_id: int = None, solo_futuros: bool = False, skip: int = 0, limit: int = 100):
        query = db.query(Evento).filter(Evento.activo == True)
        
        if anio_id:
            query = query.filter(Evento.anio_id == anio_id)
            
        if grupo_id:
            query = query.filter(
                or_(
                    Evento.grupo_id == grupo_id,
                    Evento.grupo_id == None
                )
            )
            
        if tipo_id:
            query = query.filter(Evento.tipo_id == tipo_id)
            
        # Lógica de ordenamiento separada
        if solo_futuros:
            query = query.filter(Evento.fecha >= date.today())
            # Próximos: del más cercano al más lejano
            return query.order_by(Evento.fecha.asc(), Evento.hora_inicio.asc()).offset(skip).limit(limit).all()
        else:
            # Historial: del más reciente al más antiguo (ideal para ver los últimos primero)
            return query.order_by(Evento.fecha.desc(), Evento.hora_inicio.desc()).offset(skip).limit(limit).all()
        
    @staticmethod
    def get_by_id(db: Session, evento_id: UUID):
        evento = db.query(Evento).filter(Evento.id == evento_id, Evento.activo == True).first()
        if not evento:
            raise HTTPException(status_code=404, detail="Evento no encontrado")
        return evento

    @staticmethod
    def create(db: Session, data: EventoCreate, usuario_id: UUID):
        # Validar lógica de horas
        if data.hora_inicio and data.hora_fin and data.hora_inicio >= data.hora_fin:
            raise HTTPException(status_code=400, detail="La hora de fin debe ser posterior a la hora de inicio")

        if not data.anio_id:
            anio_activo = db.query(AnioCatequetico).filter(AnioCatequetico.activo == True).first()
            if anio_activo:
                data.anio_id = anio_activo.id

        db_evento = Evento(
            **data.model_dump(),
            creado_por=usuario_id
        )
        db.add(db_evento)
        db.commit()
        db.refresh(db_evento)
        return db_evento

    @staticmethod
    def update(db: Session, evento_id: UUID, data: EventoUpdate):
        evento = EventoService.get_by_id(db, evento_id)
        
        update_data = data.model_dump(exclude_unset=True)
        
        # Validar horas si se están actualizando
        hora_ini = update_data.get('hora_inicio', evento.hora_inicio)
        hora_fin = update_data.get('hora_fin', evento.hora_fin)
        if hora_ini and hora_fin and hora_ini >= hora_fin:
            raise HTTPException(status_code=400, detail="La hora de fin debe ser posterior a la hora de inicio")

        for key, value in update_data.items():
            setattr(evento, key, value)
            
        db.commit()
        db.refresh(evento)
        return evento

    @staticmethod
    def desactivar(db: Session, evento_id: UUID):
        evento = EventoService.get_by_id(db, evento_id)
        evento.activo = False
        evento.deleted_at = datetime.utcnow()
        db.commit()
        return {"message": "Evento eliminado correctamente"}