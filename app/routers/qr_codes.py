# app/api/endpoints/qr_codes.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.dependencies.database import get_db
from app.schemas.qr_code import QrRequest, QrResponse
from app.services.qr_service import QrService

router = APIRouter(prefix="/qr", tags=["QR Codes"])

@router.post("/generar", response_model=QrResponse)
def generar_qr_asistencia(
    request: QrRequest,
    db: Session = Depends(get_db)
    # usuario_actual = Depends(get_current_user)  <- Agrega tu dependencia de auth luego
):
    """
    Genera el token seguro para dibujar el QR de asistencia en el frontend.
    """
    # TODO: Extraer usuario_id de tu token de autenticación cuando esté listo.
    # Por ahora pasamos None o un ID quemado.
    usuario_id_temporal = None 

    resultado = QrService.generar_o_obtener_qr(
        db=db,
        evento_id=request.evento_id,
        rol_generador=request.rol_generador,
        usuario_id=usuario_id_temporal
    )
    
    return resultado