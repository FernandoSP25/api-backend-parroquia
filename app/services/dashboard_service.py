from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date
from app.models.confirmante import Confirmante
from app.models.catequista import Catequista
from app.models.grupo import Grupo
from app.models.asistencia import Asistencia
from app.models.evento import Evento
from app.models.tipo_evento import TipoEvento
from app.models.catequista_grupo import CatequistaGrupo

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
        
    @staticmethod
    def obtener_metricas_catequista(db: Session, usuario_id: str):
        # 1. Encontrar al catequista y su grupo asignado
        catequista = db.query(Catequista).filter(Catequista.usuario_id == usuario_id, Catequista.activo == True).first()
        
        grupo_id = None
        grupo_nombre = "Sin grupo asignado"
        
        if catequista:
            cat_grupo = db.query(CatequistaGrupo).filter(CatequistaGrupo.catequista_id == catequista.id, CatequistaGrupo.activo == True).first()
            if cat_grupo and cat_grupo.grupo:
                grupo_id = cat_grupo.grupo_id
                grupo_nombre = cat_grupo.grupo.nombre

        # Variables por defecto
        total_jovenes = 0
        asistencia_promedio = 0.0
        jovenes_en_riesgo = 0
        proximos_eventos_db = []

        if grupo_id:
            # 2. Contar jóvenes de SU grupo
            total_jovenes = db.query(Confirmante).filter(Confirmante.grupo_id == grupo_id, Confirmante.activo == True).count()

            # 3. Asistencia Promedio solo de SU grupo
            total_asistencias = (
                db.query(Asistencia)
                .join(Confirmante, Asistencia.usuario_id == Confirmante.usuario_id)
                .filter(Confirmante.grupo_id == grupo_id)
                .count()
            )
            asistencias_validas = (
                db.query(Asistencia)
                .join(Confirmante, Asistencia.usuario_id == Confirmante.usuario_id)
                .filter(Confirmante.grupo_id == grupo_id, Asistencia.estado_id.in_([1, 2])) # 1: Asistió, 2: Tarde
                .count()
            )
            if total_asistencias > 0:
                asistencia_promedio = round((asistencias_validas / total_asistencias) * 100, 1)

            # 4. Jóvenes en riesgo (3 o más faltas, estado_id == 3)
            subquery_faltas = (
                db.query(Asistencia.usuario_id, func.count(Asistencia.id).label('total_faltas'))
                .filter(Asistencia.estado_id == 3)
                .group_by(Asistencia.usuario_id)
                .subquery()
            )
            jovenes_en_riesgo = (
                db.query(Confirmante)
                .join(subquery_faltas, Confirmante.usuario_id == subquery_faltas.c.usuario_id)
                .filter(Confirmante.grupo_id == grupo_id, Confirmante.activo == True, subquery_faltas.c.total_faltas >= 3)
                .count()
            )

            # 5. Próximos eventos (Globales o específicos de su grupo)
            hoy = date.today()
            proximos_eventos_db = (
                db.query(Evento)
                .join(TipoEvento, Evento.tipo_id == TipoEvento.id)
                .filter(
                    Evento.fecha >= hoy, 
                    Evento.activo == True,
                    (Evento.grupo_id == None) | (Evento.grupo_id == grupo_id)
                )
                .order_by(Evento.fecha.asc(), Evento.hora_inicio.asc())
                .limit(4)
                .all()
            )

        # Mapear los eventos
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
                "grupo_nombre": grupo_nombre,
                "total_jovenes": total_jovenes,
                "asistencia_promedio": asistencia_promedio,
                "jovenes_en_riesgo": jovenes_en_riesgo
            },
            "proximos_eventos": eventos_formateados
        }