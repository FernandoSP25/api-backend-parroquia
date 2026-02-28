from sqlalchemy.orm import Session
from fastapi import HTTPException
from datetime import datetime
from uuid import UUID

from app.models.asistencia import Asistencia
from app.models.qr_code import QrCode
from app.models.qr_uso_log import QrUsoLog

class AsistenciaService:

    @staticmethod
    def registrar_por_qr(db: Session, codigo_leido: str, usuario_id: UUID, ip_address: str = None):
        # 1. Validar formato del QR
        # Esperamos algo como: "SJMV-123e4567-e89b-12d3-a456-426614174000-token"
        if not codigo_leido.startswith("SJMV-") or len(codigo_leido) < 45:
            raise HTTPException(status_code=400, detail="Formato de código QR inválido.")

        # Extraemos el evento_id (los primeros 36 caracteres después del SJMV-) y el token
        resto = codigo_leido[5:] # Quitamos "SJMV-"
        evento_id_str = resto[:36]
        token_qr = resto[37:] # Todo lo que sigue después del último guion

        try:
            evento_id = UUID(evento_id_str)
        except ValueError:
            raise HTTPException(status_code=400, detail="ID de evento corrupto en el QR.")

        # 2. Buscar si el QR existe y es válido en la Base de Datos
        qr = db.query(QrCode).filter(
            QrCode.token == token_qr,
            QrCode.evento_id == evento_id,
            QrCode.activo == True
        ).first()

        if not qr:
            raise HTTPException(status_code=404, detail="Código QR no encontrado o ya fue desactivado.")

        # 3. Validar si ya expiró (El QR se refresca cada 15 min)
        if qr.expires_at < datetime.utcnow():
            raise HTTPException(status_code=400, detail="Este código QR ya expiró. Pídele al catequista que actualice la pantalla.")

        # 4. REGLA CLAVE: Validar que el joven no se haya registrado ya
        # UNIQUE(usuario_id, evento_id) en tu base de datos nos lo pide
        asistencia_previa = db.query(Asistencia).filter(
            Asistencia.usuario_id == usuario_id,
            Asistencia.evento_id == evento_id
        ).first()

        if asistencia_previa:
            raise HTTPException(status_code=400, detail="Ya registraste tu asistencia para este evento de hoy.")

        # 5. Todo OK, guardamos la asistencia
        try:
            nueva_asistencia = Asistencia(
                usuario_id=usuario_id,
                evento_id=evento_id,
                qr_id=qr.id,
                metodo="QR",
                ip_address=ip_address
            )
            db.add(nueva_asistencia)

            # Sumamos un uso al código QR
            qr.usos_actuales += 1

            # (Opcional) Guardamos un registro en tu tabla qr_uso_log para saber quién leyó qué
            log = QrUsoLog(
                qr_id=qr.id,
                usuario_id=usuario_id,
                evento_id=evento_id,
                exitoso=True,
                ip_address=ip_address
            )
            db.add(log)

            db.commit()
            db.refresh(nueva_asistencia)
            return nueva_asistencia

        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail="Error de base de datos al guardar la asistencia.")