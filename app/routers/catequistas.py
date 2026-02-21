from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.dependencies.database import get_db
from app.schemas.catequista import CatequistaCreate, CatequistaOut
from app.services.catequista_service import CatequistaService 

router = APIRouter(prefix="/catequistas", tags=["Catequistas"])

@router.post("/", response_model=CatequistaOut, status_code=status.HTTP_201_CREATED)
def crear_catequista(
    data: CatequistaCreate, 
    db: Session = Depends(get_db)
):
    # Llamada estática
    return CatequistaService.create(db, data)