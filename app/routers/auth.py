from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.dependencies.database import get_db
from app.services import auth_service
from app.schemas.auth import LoginRequest, LoginResponse # Usamos el nuevo Schema
from app.core.security import create_access_token

router = APIRouter(prefix="/auth", tags=["Autenticación"])

@router.post("/login", response_model=LoginResponse) # <--- Cambiamos el response_model
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    
    # 1. Autenticar (Usuario y Contraseña)
    user = auth_service.authenticate_user(db, login_data.email, login_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas o usuario inactivo",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 2. Obtener sus roles (La parte nueva)
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
            "roles": roles_nombres # <--- ¡Aquí va la magia!
        }
    }