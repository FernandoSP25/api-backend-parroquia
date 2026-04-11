from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm # <-- IMPORTANTE: Importamos esto
from sqlalchemy.orm import Session

from app.dependencies.database import get_db
from app.services import auth_service
from app.schemas.auth import LoginResponse
from app.core.security import create_access_token

router = APIRouter(prefix="/auth", tags=["Autenticación"])

@router.post("/login", response_model=LoginResponse)
def login(
    # Cambiamos LoginRequest por OAuth2PasswordRequestForm
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: Session = Depends(get_db)
):
    # form_data.username guardará el correo electrónico que escribas en Swagger
    user = auth_service.authenticate_user(db, email=form_data.username, password=form_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas o usuario inactivo",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 2. Obtener sus roles 
    roles_nombres = auth_service.get_user_roles(db, user.id)

    # 3. Crear el token
    access_token = create_access_token(subject=str(user.id))
    
    # 4. Retornar todo junto
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "email": user.email,
            "nombre": user.nombres,
            "roles": roles_nombres 
        }
    }