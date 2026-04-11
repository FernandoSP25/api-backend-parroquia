from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date
from app.models.confirmante import Confirmante
from app.models.catequista import Catequista
from app.models.grupo import Grupo
from app.models.asistencia import Asistencia
from app.models.evento import Evento
from app.models.tipo_evento import TipoEvento

class DashboardService:
    @staticmethod
    def obtener_metricas(db: Session):
        # 1. Contar KPIs básicos
        total_confirmantes = db.query(Confirmante).filter(Confirmante.activo == True).count()
        total_catequistas = db.query(Catequista).filter(Catequista.activo == True).count()
        total_grupos = db.query(Grupo).filter(Grupo.activo == True).count()

        # 2. Calcular Asistencia Promedio (Porcentaje de estados 1 y 2 vs Total)
        total_registros = db.query(Asistencia).count()
        # Consideramos "Asistió" a los Puntuales (1) y Tardanzas (2)
        asistencias_validas = db.query(Asistencia).filter(Asistencia.estado_id.in_([1, 2])).count()
        
        asistencia_promedio = 0.0
        if total_registros > 0:
            asistencia_promedio = round((asistencias_validas / total_registros) * 100, 1)

        # 3. Obtener Próximos Eventos (Los siguientes 4)
        hoy = date.today()
        proximos_eventos_db = (
            db.query(Evento)
            .join(TipoEvento, Evento.tipo_id == TipoEvento.id)
            .filter(Evento.fecha >= hoy, Evento.activo == True)
            .order_by(Evento.fecha.asc(), Evento.hora_inicio.asc())
            .limit(4)
            .all()
        )

        # Mapear los eventos al schema
        eventos_formateados = []
        for ev in proximos_eventos_db:
            eventos_formateados.append({
                "id": ev.id,
                "nombre": ev.nombre,
                "fecha": ev.fecha,
                "hora_inicio": ev.hora_inicio,
                "ubicacion": ev.ubicacion,
                "tipo_nombre": ev.tipo.nombre if ev.tipo else "General",
                "icono": ev.tipo.icono if ev.tipo else "📌"
            })

        return {
            "kpis": {
                "total_confirmantes": total_confirmantes,
                "total_catequistas": total_catequistas,
                "total_grupos": total_grupos,
                "asistencia_promedio": asistencia_promedio
            },
            "proximos_eventos": eventos_formateados
        }