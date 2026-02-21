import uuid
from sqlalchemy import Column, String, Boolean, Date, Time, Text, Integer, ForeignKey, DateTime, Numeric,TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base

class Evento(Base):
    __tablename__ = "eventos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    tipo_id = Column(Integer, ForeignKey("tipos_evento.id"), nullable=True)
    grupo_id = Column(UUID(as_uuid=True), ForeignKey("grupos.id"), nullable=True)
    creado_por = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=True)
    
    nombre = Column(String(150), nullable=False)
    descripcion = Column(Text, nullable=True)
    obligatorio = Column(Boolean, default=False)
    
    fecha = Column(Date, nullable=False)
    hora_inicio = Column(Time, nullable=True)
    hora_fin = Column(Time, nullable=True)
    ubicacion = Column(String(200), nullable=True)
    
    max_asistentes = Column(Integer, nullable=True)
    requiere_confirmacion = Column(Boolean, default=False)
    
    activo = Column(Boolean, default=True)
    deleted_at = Column(TIMESTAMP, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    latitud = Column(Numeric(10, 8), nullable=True)
    longitud = Column(Numeric(11, 8), nullable=True)
    # Relaciones
    tipo = relationship("TipoEvento") 
    grupo = relationship("Grupo", back_populates="eventos")
    creador = relationship("Usuario")
    
    # Relación con asistencias y QRs
    asistencias = relationship("Asistencia", back_populates="evento")
    qrs = relationship("QrCode", back_populates="evento")