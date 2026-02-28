from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.dependencies.database import get_db
from app.dependencies.auth import get_current_active_user
from app.models.usuario import Usuario
from app.schemas.asistencia import AsistenciaQRRequest, AsistenciaResponse
from app.services.asistencia_service import AsistenciaService

router = APIRouter(prefix="/asistencias", tags=["Control de Asistencias"])

@router.post("/qr", response_model=AsistenciaResponse)
def registrar_asistencia_qr(
    data: AsistenciaQRRequest,
    request: Request, # Para sacar la IP del celular si están en la parroquia
    db: Session = Depends(get_db),
    # El token JWT que manda Next.js nos dirá mágicamente qué Confirmante es
    current_user: Usuario = Depends(get_current_active_user) 
):
    ip_address = request.client.host
    
    asistencia = AsistenciaService.registrar_por_qr(
        db=db,
        codigo_leido=data.codigo_leido,
        usuario_id=current_user.id,
        ip_address=ip_address
    )
    
    return {
        "id": asistencia.id,
        "evento_id": asistencia.evento_id,
        "fecha": asistencia.fecha,
        "metodo": asistencia.metodo,
        "mensaje": "¡Llegada confirmada correctamente!"
    }