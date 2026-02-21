from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.dependencies.database import get_db
from app.dependencies.auth import RoleChecker
from app.schemas.admin import AdminCreate, AdminOut
from app.services.admin_service import AdminService

router = APIRouter(prefix="/admins", tags=["Administradores"])

@router.post("/", response_model=AdminOut, status_code=status.HTTP_201_CREATED)
def crear_admin(
    data: AdminCreate, 
    db: Session = Depends(get_db),
    # current_user = Depends(allow_super_admin) # Descomentar si quieres restringirlo
):
    return AdminService.create(db, data)