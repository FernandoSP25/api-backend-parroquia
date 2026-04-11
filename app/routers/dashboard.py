from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.dependencies.database import get_db
from app.dependencies.auth import get_current_active_user
from app.models.usuario import Usuario
from app.schemas.dashboard import DashboardResponse
from app.services.dashboard_service import DashboardService

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/resumen", response_model=DashboardResponse)
def obtener_resumen_dashboard(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Obtiene todos los KPIs y datos necesarios para pintar la pantalla de inicio (Dashboard).
    """
    return DashboardService.obtener_metricas(db)