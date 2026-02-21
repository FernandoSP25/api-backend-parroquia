import uuid
from sqlalchemy import Column, String, Date, Boolean, ForeignKey, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base

class CatequistaGrupo(Base):
    __tablename__ = "catequista_grupo"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    catequista_id = Column(UUID(as_uuid=True), ForeignKey("catequistas.id", ondelete="CASCADE"), nullable=False)
    grupo_id = Column(UUID(as_uuid=True), ForeignKey("grupos.id", ondelete="CASCADE"), nullable=False)
    
    rol_interno = Column(String(100), nullable=True)
    fecha_asignacion = Column(Date, server_default=func.current_date())
    
    activo = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, server_default=func.now())

    # --- RELACIONES ---
    
    # ⚠️ AQUÍ EL CAMBIO: Agrega back_populates="grupos_asignados"
    catequista = relationship("Catequista", back_populates="grupos_asignados")
    
    grupo = relationship("Grupo", back_populates="catequistas_asignados")