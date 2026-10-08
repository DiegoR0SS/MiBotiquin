from fastapi import APIRouter, HTTPException
from database import obtener_conexion
from datetime import datetime
from decimal import Decimal
from models.toma import TomaCrear, TomaConfirmar

router = APIRouter(
    prefix="/tomas",
    tags=["Tomas"]
)


@router.post("")
def crear_toma(toma: TomaCrear):
    conexion = obtener_conexion()

    try:
        with conexion.cursor() as cursor:
            cursor.execute(
                """
                SELECT id_horario, hora
                FROM horarios_toma
                WHERE id_horario = %s
                  AND activo = TRUE;
                """,
                (toma.id_horario,)
            )

            horario = cursor.fetchone()

            if horario is None:
                raise HTTPException(
                    status_code=404,
                    detail="Horario no encontrado o inactivo"
                )

            if toma.fecha_programada.time() != horario[1]:
                raise HTTPException(
                    status_code=400,
                    detail="La hora programada no coincide con el horario"
                )

            cursor.execute(
                """
                SELECT id_toma
                FROM historial_tomas
                WHERE id_horario = %s
                  AND fecha_programada = %s;
                """,
                (
                    toma.id_horario,
                    toma.fecha_programada
                )
            )

            if cursor.fetchone() is not None:
                raise HTTPException(
                    status_code=409,
                    detail="Esta toma ya está registrada"
                )

            cursor.execute(
                """
                INSERT INTO historial_tomas (
                    id_horario,
                    fecha_programada,
                    estado
                )
                VALUES (%s, %s, 'PENDIENTE')
                RETURNING id_toma;
                """,
                (
                    toma.id_horario,
                    toma.fecha_programada
                )
            )

            id_toma = cursor.fetchone()[0]

            conexion.commit()

            return {
                "mensaje": "Toma programada correctamente",
                "id_toma": id_toma,
                "estado": "PENDIENTE"
            }

    except HTTPException:
        conexion.rollback()
        raise

    except Exception:
        conexion.rollback()
        raise

    finally:
        conexion.close()

@router.post("/{id_toma}/confirmar")
def confirmar_toma(id_toma: int, confirmacion: TomaConfirmar):
    conexion = obtener_conexion()

    try:
        with conexion.cursor() as cursor:

            cursor.execute(
                """
                SELECT
                    ht.id_toma,
                    ht.estado,
                    ht.fecha_programada,
                    tm.id_medicamento,
                    tm.cantidad_dosis,
                    tm.unidad_dosis,
                    t.id_usuario,
                    t.estado
                FROM historial_tomas ht
                JOIN horarios_toma h
                    ON h.id_horario = ht.id_horario
                JOIN tratamiento_medicamentos tm
                    ON tm.id_tratamiento_medicamento =
                       h.id_tratamiento_medicamento
                JOIN tratamientos t
                    ON t.id_tratamiento = tm.id_tratamiento
                WHERE ht.id_toma = %s
                FOR UPDATE OF ht;
                """,
                (id_toma,)
            )

            toma = cursor.fetchone()

            if toma is None:
                raise HTTPException(
                    status_code=404,
                    detail="Toma no encontrada"
                )

            estado_toma = toma[1]
            id_medicamento = toma[3]
            cantidad_dosis = toma[4]
            unidad_dosis = toma[5]
            id_usuario = toma[6]
            estado_tratamiento = toma[7]

            if estado_toma != "PENDIENTE":
                raise HTTPException(
                    status_code=409,
                    detail="Esta toma ya fue procesada"
                )

            if estado_tratamiento != "ACTIVO":
                raise HTTPException(
                    status_code=400,
                    detail="El tratamiento no está activo"
                )

            cursor.execute(
                """
                SELECT
                    id_inventario,
                    lote,
                    fecha_caducidad,
                    contenido_actual,
                    unidad_contenido
                FROM inventario
                WHERE id_usuario = %s
                  AND id_medicamento = %s
                  AND contenido_actual > 0
                ORDER BY
                    fecha_caducidad ASC NULLS LAST,
                    id_inventario ASC
                FOR UPDATE;
                """,
                (id_usuario, id_medicamento)
            )

            lotes = cursor.fetchall()

            if not lotes:
                raise HTTPException(
                    status_code=400,
                    detail="No hay existencias disponibles"
                )

            unidades = {
                lote[4].strip().upper()
                for lote in lotes
            }

            if (
                len(unidades) != 1
                or unidad_dosis.strip().upper() not in unidades
            ):
                raise HTTPException(
                    status_code=400,
                    detail="La unidad de la dosis no coincide con el inventario"
                )

            cantidad_consumir = Decimal(str(cantidad_dosis))

            existencia_total = sum(
                (lote[3] for lote in lotes),
                Decimal("0")
            )

            if existencia_total < cantidad_consumir:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        f"Existencias insuficientes. "
                        f"Disponible: {existencia_total} {unidad_dosis}"
                    )
                )

            cantidad_restante = cantidad_consumir
            lotes_utilizados = []

            for lote in lotes:
                if cantidad_restante <= 0:
                    break

                id_inventario = lote[0]
                numero_lote = lote[1]
                contenido_actual = lote[3]

                cantidad_descontar = min(
                    contenido_actual,
                    cantidad_restante
                )

                nuevo_contenido = (
                    contenido_actual - cantidad_descontar
                )

                cursor.execute(
                    """
                    UPDATE inventario
                    SET contenido_actual = %s
                    WHERE id_inventario = %s;
                    """,
                    (nuevo_contenido, id_inventario)
                )

                lotes_utilizados.append({
                    "id_inventario": id_inventario,
                    "lote": numero_lote,
                    "cantidad_descontada": cantidad_descontar,
                    "contenido_restante": nuevo_contenido
                })

                cantidad_restante -= cantidad_descontar

            cursor.execute(
                """
                UPDATE historial_tomas
                SET
                    estado = 'TOMADA',
                    fecha_tomada = %s,
                    cantidad_consumida = %s,
                    unidad_consumida = %s,
                    observaciones = %s
                WHERE id_toma = %s;
                """,
                (
                    datetime.now(),
                    cantidad_consumir,
                    unidad_dosis,
                    confirmacion.observaciones,
                    id_toma
                )
            )

            conexion.commit()

            return {
                "mensaje": "Toma confirmada correctamente",
                "id_toma": id_toma,
                "estado": "TOMADA",
                "id_medicamento": id_medicamento,
                "cantidad_consumida": cantidad_consumir,
                "unidad_consumida": unidad_dosis,
                "lotes_utilizados": lotes_utilizados
            }

    except HTTPException:
        conexion.rollback()
        raise

    except Exception:
        conexion.rollback()
        raise

    finally:
        conexion.close()
