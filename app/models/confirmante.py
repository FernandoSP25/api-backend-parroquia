import uuid
from sqlalchemy import Column, String, Boolean, Date, ForeignKey, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base

class Confirmante(Base):
    __tablename__ = "confirmantes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Relaciones
    usuario_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id", ondelete="CASCADE"), unique=True, nullable=False)
    grupo_id = Column(UUID(as_uuid=True), ForeignKey("grupos.id"), nullable=True)
    anio_id = Column(UUID(as_uuid=True), ForeignKey("anios_catequeticos.id"), nullable=True)

    # Familia / Apoderado
    apoderado_nombre = Column(String(150), nullable=True)
    apoderado_telefono = Column(String(20), nullable=True)
    apoderado_email = Column(String(150), nullable=True)
    apoderado_relacion = Column(String(50), default="PADRE")

    # Padrino
    nombre_padrino = Column(String(150), nullable=True)
    telefono_padrino = Column(String(20), nullable=True)
    email_padrino = Column(String(150), nullable=True)

    # Sacramentos
    bautizado = Column(Boolean, default=True)
    parroquia_bautismo = Column(String(150), nullable=True)
    fecha_bautismo = Column(Date, nullable=True)
    libro_bautismo = Column(String(50), nullable=True)
    folio_bautismo = Column(String(50), nullable=True)

    # Control
    activo = Column(Boolean, default=True)
    fecha_inscripcion = Column(Date, server_default=func.current_date())
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # Relaciones ORM
    usuario = relationship("Usuario", back_populates="confirmante_perfil")
    grupo = relationship("Grupo", back_populates="confirmantes")
    anio = relationship("AnioCatequetico", back_populates="confirmantes")
    notas = relationship("Nota", back_populates="confirmante") # Descomenta si tienes Notas