from sqlalchemy.orm import Session, joinedload
from uuid import UUID
from datetime import date
from dateutil.relativedelta import relativedelta
from fastapi import HTTPException
from sqlalchemy import or_
from app.models.grupo import Grupo
from app.models.confirmante import Confirmante
from app.models.catequista_grupo import CatequistaGrupo
from app.models.usuario import Usuario
from app.models.catequista import Catequista

class GrupoService:

    @staticmethod
    def obtener_tablero(db: Session, anio_id: UUID):
        # 1. Obtener Grupos del Año (con relaciones cargadas)
        grupos_db = db.query(Grupo).options(
            # Relación: grupo -> catequistas_asociados -> catequista -> usuario
            joinedload(Grupo.catequistas_asignados)
                .joinedload(CatequistaGrupo.catequista)
                .joinedload(Catequista.usuario),
            # Relación: grupo -> confirmantes -> usuario
            joinedload(Grupo.confirmantes)
                .joinedload(Confirmante.usuario)
        ).filter(
            Grupo.anio_id == anio_id,
            Grupo.activo == True
        ).all()

        # 2. Obtener Confirmantes DISPONIBLES (Sin grupo)
        # Traemos los del año actual O los que no tienen año asignado aún
        sin_grupo_conf = db.query(Confirmante).options(joinedload(Confirmante.usuario)).filter(
            or_(Confirmante.anio_id == anio_id, Confirmante.anio_id == None),
            Confirmante.grupo_id == None,
            Confirmante.activo == True
        ).all()

        # 3. Obtener Catequistas DISPONIBLES
        # (Lógica: Todos los activos MENOS los que ya están en un grupo de este año)
        
        # A. Todos los catequistas
        all_catequistas = db.query(Catequista).options(joinedload(Catequista.usuario)).filter(
            Catequista.activo == True
        ).all()
        
        # B. IDs de catequistas ocupados en ESTE año (revisando los grupos que ya trajimos)
        ids_ocupados = set()
        for g in grupos_db:
            for cg in g.catequistas_asignados:
                if cg.activo:
                    ids_ocupados.add(cg.catequista_id)
        
        # C. Filtrar (Disponibles = Todos - Ocupados)
        catequistas_disponibles = [c for c in all_catequistas if c.id not in ids_ocupados]


        # --- FORMATEO Y MEZCLA ---
        pool_sin_asignar = []

        # A. Formatear Catequistas para el Pool
        for cat in catequistas_disponibles:
            pool_sin_asignar.append({
                "tipo": "CATEQUISTA",  # 👈 IMPORTANTE PARA EL FRONTEND
                "id": cat.id,          # ID del Catequista (ojo, no del usuario)
                "nombres": cat.usuario.nombres,
                "apellidos": cat.usuario.apellidos,
                "foto_url": cat.usuario.foto_url,
                "edad": 0, # No relevante para profes
                "rol_interno": "Sin Asignar"
            })

        # B. Formatear Confirmantes para el Pool
        for conf in sin_grupo_conf:
            edad = relativedelta(date.today(), conf.usuario.fecha_nacimiento).years if conf.usuario.fecha_nacimiento else 0
            pool_sin_asignar.append({
                "tipo": "CONFIRMANTE", # 👈 IMPORTANTE PARA EL FRONTEND
                "id": conf.id,         # ID del Confirmante
                "nombres": conf.usuario.nombres,
                "apellidos": conf.usuario.apellidos,
                "foto_url": conf.usuario.foto_url,
                "edad": edad
            })

        # C. Formatear Grupos (Columnas)
        lista_grupos = []
        for g in grupos_db:
            # Lista de Profes dentro del grupo
            cats_en_grupo = []
            for cg in g.catequistas_asignados:
                if cg.activo:
                    cats_en_grupo.append({
                        "id": cg.catequista.id,
                        "nombres": cg.catequista.usuario.nombres,
                        "apellidos": cg.catequista.usuario.apellidos,
                        "foto_url": cg.catequista.usuario.foto_url,
                        "tipo": "CATEQUISTA"
                    })

            # Lista de Alumnos dentro del grupo
            confs_en_grupo = []
            for c in g.confirmantes:
                if c.activo:
                    edad = relativedelta(date.today(), c.usuario.fecha_nacimiento).years if c.usuario.fecha_nacimiento else 0
                    confs_en_grupo.append({
                        "id": c.id,
                        "nombres": c.usuario.nombres,
                        "apellidos": c.usuario.apellidos,
                        "edad": edad,
                        "foto_url": c.usuario.foto_url,
                        "tipo": "CONFIRMANTE"
                    })

            lista_grupos.append({
                "id": g.id,
                "nombre": g.nombre,
                "capacidad_maxima": g.capacidad_maxima,
                "total_inscritos": len(confs_en_grupo),
                "catequistas": cats_en_grupo,
                "confirmantes": confs_en_grupo
            })

        # ========================================================
        # ✅ ALINEADO A LA IZQUIERDA - TOTALMENTE FUERA DEL FOR
        # ========================================================
        pool_confirmantes = [item for item in pool_sin_asignar if item["tipo"] == "CONFIRMANTE"]
        pool_catequistas = [item for item in pool_sin_asignar if item["tipo"] == "CATEQUISTA"]

        return {
            "sin_asignar_confirmantes": pool_confirmantes,
            "sin_asignar_catequistas": pool_catequistas,
            "grupos": lista_grupos
        }

    # --- MOVIMIENTO DRAG & DROP ---
    @staticmethod
    def mover_confirmante(db: Session, confirmante_id: UUID, nuevo_grupo_id: UUID | None):
        # ... (Tu código de movimiento estaba perfecto, mantenlo igual) ...
        confirmante = db.query(Confirmante).filter(Confirmante.id == confirmante_id).first()
        if not confirmante:
            raise HTTPException(status_code=404, detail="Confirmante no encontrado")

        if nuevo_grupo_id:
            grupo = db.query(Grupo).filter(Grupo.id == nuevo_grupo_id).first()
            if not grupo:
                raise HTTPException(status_code=404, detail="Grupo destino no encontrado")
            
            total = db.query(Confirmante).filter(
                Confirmante.grupo_id == nuevo_grupo_id, 
                Confirmante.activo == True
            ).count()
            
            if total >= grupo.capacidad_maxima:
                raise HTTPException(status_code=400, detail=f"Grupo lleno ({grupo.capacidad_maxima})")

        confirmante.grupo_id = nuevo_grupo_id
        db.add(confirmante)
        db.commit()
        return {"message": "Movimiento exitoso", "grupo_id": nuevo_grupo_id}
    
    @staticmethod
    def mover_catequista(db: Session, catequista_id: UUID, nuevo_grupo_id: UUID | None):
        """
        Mueve un catequista de un grupo a otro (o a 'Sin Asignar').
        """
        # 1. Validar Catequista
        catequista = db.query(Catequista).filter(Catequista.id == catequista_id).first()
        if not catequista:
            raise HTTPException(status_code=404, detail="Catequista no encontrado")

        # 2. Desactivar cualquier asignación ACTIVA que tenga el catequista actualmente
        # (Usamos .update() directo para que sea más rápido y limpio)
        db.query(CatequistaGrupo).filter(
            CatequistaGrupo.catequista_id == catequista_id,
            CatequistaGrupo.activo == True
        ).update({"activo": False})

        # 3. Asignar al nuevo grupo (si no es 'Sin Asignar')
        if nuevo_grupo_id:
            # Validar que el grupo exista
            grupo = db.query(Grupo).filter(Grupo.id == nuevo_grupo_id).first()
            if not grupo:
                raise HTTPException(status_code=404, detail="Grupo destino no encontrado")

            # 🔑 EL TRUCO: Buscar si ya existe una relación histórica con este grupo
            asignacion_existente = db.query(CatequistaGrupo).filter(
                CatequistaGrupo.catequista_id == catequista_id,
                CatequistaGrupo.grupo_id == nuevo_grupo_id
            ).first()

            if asignacion_existente:
                # Si ya estuvo en este grupo antes, solo lo reactivamos (UPDATE)
                asignacion_existente.activo = True
            else:
                # Si es la primera vez en este grupo, creamos el registro (INSERT)
                nueva_asignacion = CatequistaGrupo(
                    catequista_id=catequista_id,
                    grupo_id=nuevo_grupo_id,
                    rol_interno="Catequista",
                    activo=True
                )
                db.add(nueva_asignacion)

        db.commit()
        return {"message": "Catequista reasignado correctamente"}