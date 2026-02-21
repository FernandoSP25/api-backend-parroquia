from sqlalchemy import Column, Integer, String, Boolean
from app.db.base import Base
from sqlalchemy.orm import relationship

class TipoTelefono(Base):
    __tablename__ = "tipos_telefono"

    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String(30), unique=True, nullable=False)
    nombre = Column(String(50), nullable=False)
    activo = Column(Boolean, default=True)
    
    telefonos = relationship("Telefono", back_populates="tipo")
    
