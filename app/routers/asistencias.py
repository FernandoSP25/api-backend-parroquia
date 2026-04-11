from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.dependencies.database import get_db
from app.dependencies.auth import get_current_active_user, RoleChecker
from app.models.usuario import Usuario
from app.schemas.asistencia import AsistenciaResponse, AsistenciaBulkRequest
from app.services.asistencia_service import AsistenciaService
from app.schemas.asistencia import AlumnoChecklist

router = APIRouter(prefix="/asistencias", tags=["Control de Asistencias"])

# Control de seguridad: Solo estos roles pueden pasar asistencia
permitir_asistencia = RoleChecker(["ADMIN", "CATEQUISTA"])

@router.get("/evento/{evento_id}", response_model=List[AsistenciaResponse])
def ver_asistencia_evento(
    evento_id: UUID,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user) # Todos pueden verla (Confirmantes incluidos)
):
    """Obtiene la lista de asistencias de un evento"""
    return AsistenciaService.obtener_por_evento(db, evento_id)

@router.put("/evento/{evento_id}/masiva", response_model=List[AsistenciaResponse])
def registrar_asistencia_checklist(
    evento_id: UUID,
    data: AsistenciaBulkRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(permitir_asistencia) # Solo catequista/admin
):
    """Guarda la lista completa de asistencias de un aula"""
    ip_address = request.client.host
    
    return AsistenciaService.registrar_asistencia_masiva(
        db=db,
        evento_id=evento_id,
        catequista_id=current_user.id,
        asistencias_data=data.asistencias,
        ip_address=ip_address
    )
    
@router.get("/evento/{evento_id}/checklist", response_model=List[AlumnoChecklist])
def obtener_lista_asistencia(
    evento_id: UUID,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(permitir_asistencia) # Catequista o Admin
):
    """Devuelve la lista de alumnos del catequista con su estado de asistencia actual (o Falta por defecto)"""
    return AsistenciaService.obtener_checklist_evento(db, evento_id, current_user)