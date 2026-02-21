from sqlalchemy import Column, Integer, String, Boolean, Text
from sqlalchemy.orm import relationship # <--- Necesario para relacionar
from app.db.base import Base

# CAMBIO AQUÍ: TipoQR -> TipoQr
class TipoQr(Base):
    __tablename__ = "tipos_qr"

    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String(30), unique=True, nullable=False)
    nombre = Column(String(100), nullable=False)
    
    # En tu SQL es TEXT, así que usa Text aquí también
    descripcion = Column(Text, nullable=True)
    
    activo = Column(Boolean, default=True)

    # Relación inversa (para que funcione QrCode.tipo)
    qrs = relationship("QrCode", back_populates="tipo")