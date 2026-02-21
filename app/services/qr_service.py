# app/services/qr_service.py
import secrets
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from uuid import UUID
from fastapi import HTTPException

from app.models.qr_code import QrCode
from app.models.tipo_qr import TipoQr 

class QrService:
    @staticmethod
    def generar_o_obtener_qr(db: Session, evento_id: UUID, rol_generador: str, usuario_id: UUID = None):
        """
        Genera un código QR dinámico para un evento, o devuelve el existente si aún es válido.
        Mapea el rol del generador al tipo de QR correspondiente.
        """
        
        # 1. Mapeo de lógica de negocio: 
        # Admin genera para Catequistas, Catequista genera para Confirmantes.
        codigo_buscado = "CATEQUISTA" if rol_generador == "ADMIN" else "CONFIRMANTE"
        
        # Uso del ORM en lugar de SQL crudo para buscar el tipo
        tipo_qr = db.query(TipoQr).filter(TipoQr.codigo == codigo_buscado).first()
        
        if not tipo_qr:
            raise HTTPException(
                status_code=500, 
                detail=f"Configuración de catálogo faltante: Tipo QR '{codigo_buscado}' no encontrado."
            )

        # 2. Buscar si ya existe un QR vigente
        # Optimizamos la query para buscar exactamente lo que necesitamos
        ahora = datetime.utcnow()
        qr_existente = db.query(QrCode).filter(
            QrCode.evento_id == evento_id,
            QrCode.tipo_id == tipo_qr.id,
            QrCode.activo == True,
            QrCode.expires_at > ahora
        ).first()

        if qr_existente:
            return {
                "token_completo": f"SJMV-{evento_id}-{qr_existente.token}",
                "expires_at": qr_existente.expires_at
            }

        # 3. Creación de nuevo token si no hay uno válido
        try:
            nuevo_token = secrets.token_hex(16) # 32 caracteres seguros
            
            fecha_expiracion = ahora + timedelta(minutes=15)

            nuevo_qr = QrCode(
                tipo_id=tipo_qr.id,
                evento_id=evento_id,
                created_by=usuario_id,
                token=nuevo_token,
                expires_at=fecha_expiracion,
                activo=True
        )

            db.add(nuevo_qr)
            db.commit()
            db.refresh(nuevo_qr)

            return {
                "token_completo": f"SJMV-{evento_id}-{nuevo_qr.token}",
                "expires_at": nuevo_qr.expires_at
            }
            
        except Exception as e:
            db.rollback()
            print("🔥 ERROR REAL:", e)
            raise HTTPException(
                status_code=500,
                detail=str(e)
            )