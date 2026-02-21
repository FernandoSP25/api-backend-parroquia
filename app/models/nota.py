import uuid
from sqlalchemy import Column, String, Numeric, Text, Date, ForeignKey, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base

class Nota(Base):
    __tablename__ = "notas"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    confirmante_id = Column(UUID(as_uuid=True), ForeignKey("confirmantes.id", ondelete="CASCADE"), nullable=False)
    registrada_por = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=True)
    
    curso = Column(String(100), nullable=False)
    nota = Column(Numeric(4, 2), nullable=True) # El Check (0-20) se hace en base de datos
    observacion = Column(Text, nullable=True)
    
    fecha = Column(Date, server_default=func.current_date())
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # Relaciones
    confirmante = relationship("Confirmante", back_populates="notas")
    registrador = relationship("Usuario") # Quién puso la nota