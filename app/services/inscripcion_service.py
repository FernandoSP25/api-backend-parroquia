from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.inscripcion import Inscripcion
from app.schemas.inscripcion import InscripcionCreate, InscripcionUpdate
from datetime import date

class InscripcionService:

    @staticmethod
    def calcular_edad(nacimiento: date) -> int:
        hoy = date.today()
        # Resta años y ajusta si aún no ha pasado el cumpleaños este año
        return hoy.year - nacimiento.year - ((hoy.month, hoy.day) < (nacimiento.month, nacimiento.day))
    
    @staticmethod
    def create(db: Session, data: InscripcionCreate):
        # 1. Validar duplicados por DNI
        existing = db.query(Inscripcion).filter(Inscripcion.dni == data.dni).first()
        if existing:
            raise HTTPException(status_code=400, detail="Ya existe una inscripción con este DNI.")

        # 2. CALCULAR EDAD AUTOMÁTICAMENTE
        edad_calculada = InscripcionService.calcular_edad(data.fecha_nacimiento)

        # 3. Validar edad mínima (Opcional, pero recomendado)
        if edad_calculada < 14:
            raise HTTPException(status_code=400, detail=f"Debes tener al menos 14 años. Tienes {edad_calculada}.")

        # 4. Crear objeto DB (Inyectamos la edad calculada)
        nueva_inscripcion = Inscripcion(
            **data.model_dump(),
            edad=edad_calculada  # <-- Aquí guardamos el cálculo en la BD
        )
        
        db.add(nueva_inscripcion)
        db.commit()
        db.refresh(nueva_inscripcion)
        return nueva_inscripcion

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100):
        return db.query(Inscripcion).order_by(Inscripcion.fecha_registro.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def get_by_id(db: Session, inscripcion_id: int):
        return db.query(Inscripcion).filter(Inscripcion.id == inscripcion_id).first()

    @staticmethod
    def update(db: Session, inscripcion_id: int, data: InscripcionUpdate):
        inscripcion = db.query(Inscripcion).filter(Inscripcion.id == inscripcion_id).first()
        if not inscripcion:
            raise HTTPException(status_code=404, detail="Inscripción no encontrada")

        update_data = data.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(inscripcion, field, value)

        db.add(inscripcion)
        db.commit()
        db.refresh(inscripcion)
        return inscripcion