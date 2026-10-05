from fastapi import APIRouter, HTTPException

from database import obtener_conexion
from models.inventario import InventarioCrear, InventarioActualizar, EntradaInventario, ConsumoInventario
from decimal import Decimal

router = APIRouter(
    prefix="/inventario",
    tags=["Inventario"]
)


@router.post("")
def agregar_inventario(inventario: InventarioCrear):
    conexion = obtener_conexion()

    try:
        with conexion.cursor() as cursor:
            cursor.execute(
                """
                SELECT id_usuario
                FROM usuarios
                WHERE id_usuario = %s;
                """,
                (inventario.id_usuario,)
            )

            if cursor.fetchone() is None:
                raise HTTPException(
                    status_code=404,
                    detail="Usuario no encontrado"
                )

            cursor.execute(
                """
                SELECT id_medicamento
                FROM medicamentos
                WHERE id_medicamento = %s;
                """,
                (inventario.id_medicamento,)
            )

            if cursor.fetchone() is None:
                raise HTTPException(
                    status_code=404,
                    detail="Medicamento no encontrado"
                )

            contenido_actual = (
                inventario.cantidad_envases
                * inventario.contenido_por_envase
            )

            cursor.execute(
                """
                INSERT INTO inventario (
                    id_usuario,
                    id_medicamento,
                    lote,
                    fecha_caducidad,
                    cantidad_envases,
                    tipo_envase,
                    contenido_por_envase,
                    unidad_contenido,
                    contenido_actual,
                    nivel_minimo
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id_inventario;
                """,
                (
                    inventario.id_usuario,
                    inventario.id_medicamento,
                    inventario.lote,
                    inventario.fecha_caducidad,
                    inventario.cantidad_envases,
                    inventario.tipo_envase,
                    inventario.contenido_por_envase,
                    inventario.unidad_contenido,
                    contenido_actual,
                    inventario.nivel_minimo
                )
            )

            id_inventario = cursor.fetchone()[0]

            conexion.commit()

            return {
                "mensaje": "Medicamento agregado al inventario correctamente",
                "id_inventario": id_inventario,
                "contenido_actual": contenido_actual,
                "unidad_contenido": inventario.unidad_contenido
            }

    except HTTPException:
        conexion.rollback()
        raise

    except Exception:
        conexion.rollback()
        raise

    finally:
        conexion.close()

@router.get("/usuario/{id_usuario}")
def obtener_inventario_usuario(id_usuario: int):
    conexion = obtener_conexion()

    try:
        with conexion.cursor() as cursor:
            cursor.execute(
                """
                SELECT id_usuario
                FROM usuarios
                WHERE id_usuario = %s;
                """,
                (id_usuario,)
            )

            if cursor.fetchone() is None:
                raise HTTPException(
                    status_code=404,
                    detail="Usuario no encontrado"
                )

            cursor.execute(
                """
                SELECT
                    i.id_inventario,
                    i.id_medicamento,
                    m.nombre_comercial,
                    i.lote,
                    i.fecha_caducidad,
                    i.cantidad_envases,
                    i.tipo_envase,
                    i.contenido_por_envase,
                    i.unidad_contenido,
                    i.contenido_actual,
                    i.nivel_minimo
                FROM inventario i
                JOIN medicamentos m
                    ON m.id_medicamento = i.id_medicamento
                WHERE i.id_usuario = %s
                ORDER BY
                    i.fecha_caducidad ASC NULLS LAST,
                    m.nombre_comercial ASC;
                """,
                (id_usuario,)
            )

            inventario = cursor.fetchall()

            resultado = []

            for registro in inventario:
                resultado.append({
                    "id_inventario": registro[0],
                    "id_medicamento": registro[1],
                    "nombre_comercial": registro[2],
                    "lote": registro[3],
                    "fecha_caducidad": registro[4],
                    "cantidad_envases": registro[5],
                    "tipo_envase": registro[6],
                    "contenido_por_envase": registro[7],
                    "unidad_contenido": registro[8],
                    "contenido_actual": registro[9],
                    "nivel_minimo": registro[10]
                })

            return resultado

    finally:
        conexion.close()

@router.get("/{id_inventario}")
def obtener_inventario(id_inventario: int):
    conexion = obtener_conexion()

    try:
        with conexion.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    i.id_inventario,
                    i.id_usuario,
                    i.id_medicamento,
                    m.nombre_comercial,
                    i.lote,
                    i.fecha_caducidad,
                    i.cantidad_envases,
                    i.tipo_envase,
                    i.contenido_por_envase,
                    i.unidad_contenido,
                    i.contenido_actual,
                    i.nivel_minimo
                FROM inventario i
                JOIN medicamentos m
                    ON m.id_medicamento = i.id_medicamento
                WHERE i.id_inventario = %s;
                """,
                (id_inventario,)
            )

            registro = cursor.fetchone()

            if registro is None:
                raise HTTPException(
                    status_code=404,
                    detail="Registro de inventario no encontrado"
                )

            return {
                "id_inventario": registro[0],
                "id_usuario": registro[1],
                "id_medicamento": registro[2],
                "nombre_comercial": registro[3],
                "lote": registro[4],
                "fecha_caducidad": registro[5],
                "cantidad_envases": registro[6],
                "tipo_envase": registro[7],
                "contenido_por_envase": registro[8],
                "unidad_contenido": registro[9],
                "contenido_actual": registro[10],
                "nivel_minimo": registro[11]
            }

    finally:
        conexion.close()

@router.put("/{id_inventario}")
def actualizar_inventario(
    id_inventario: int,
    inventario: InventarioActualizar
):
    conexion = obtener_conexion()

    try:
        with conexion.cursor() as cursor:
            cursor.execute(
                """
                UPDATE inventario
                SET
                    lote = %s,
                    fecha_caducidad = %s,
                    cantidad_envases = %s,
                    tipo_envase = %s,
                    contenido_por_envase = %s,
                    unidad_contenido = %s,
                    nivel_minimo = %s
                WHERE id_inventario = %s
                RETURNING id_inventario;
                """,
                (
                    inventario.lote,
                    inventario.fecha_caducidad,
                    inventario.cantidad_envases,
                    inventario.tipo_envase,
                    inventario.contenido_por_envase,
                    inventario.unidad_contenido,
                    inventario.nivel_minimo,
                    id_inventario
                )
            )

            resultado = cursor.fetchone()

            if resultado is None:
                conexion.rollback()

                raise HTTPException(
                    status_code=404,
                    detail="Registro de inventario no encontrado"
                )

            conexion.commit()

            return {
                "mensaje": "Inventario actualizado correctamente",
                "id_inventario": id_inventario
            }

    except HTTPException:
        conexion.rollback()
        raise

    except Exception:
        conexion.rollback()
        raise

    finally:
        conexion.close()

@router.post("/{id_inventario}/entrada")
def agregar_existencias(
    id_inventario: int,
    entrada: EntradaInventario
):
    conexion = obtener_conexion()

    try:
        with conexion.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    cantidad_envases,
                    contenido_por_envase,
                    contenido_actual,
                    unidad_contenido
                FROM inventario
                WHERE id_inventario = %s
                FOR UPDATE;
                """,
                (id_inventario,)
            )

            registro = cursor.fetchone()

            if registro is None:
                raise HTTPException(
                    status_code=404,
                    detail="Registro de inventario no encontrado"
                )

            cantidad_envases_actual = registro[0]
            contenido_por_envase = registro[1]
            contenido_actual = registro[2]
            unidad_contenido = registro[3]

            contenido_agregado = (
                entrada.cantidad_envases * contenido_por_envase
            )

            nueva_cantidad_envases = (
                cantidad_envases_actual + entrada.cantidad_envases
            )

            nuevo_contenido_actual = (
                contenido_actual + contenido_agregado
            )

            cursor.execute(
                """
                UPDATE inventario
                SET
                    cantidad_envases = %s,
                    contenido_actual = %s
                WHERE id_inventario = %s;
                """,
                (
                    nueva_cantidad_envases,
                    nuevo_contenido_actual,
                    id_inventario
                )
            )

            conexion.commit()

            return {
                "mensaje": "Existencias agregadas correctamente",
                "id_inventario": id_inventario,
                "envases_agregados": entrada.cantidad_envases,
                "contenido_agregado": contenido_agregado,
                "cantidad_envases": nueva_cantidad_envases,
                "contenido_actual": nuevo_contenido_actual,
                "unidad_contenido": unidad_contenido
            }

    except HTTPException:
        conexion.rollback()
        raise

    except Exception:
        conexion.rollback()
        raise

    finally:
        conexion.close()

@router.post("/consumo")
def consumir_medicamento(consumo: ConsumoInventario):
    conexion = obtener_conexion()

    try:
        with conexion.cursor() as cursor:

            cursor.execute(
                """
                SELECT id_usuario
                FROM usuarios
                WHERE id_usuario = %s;
                """,
                (consumo.id_usuario,)
            )

            if cursor.fetchone() is None:
                raise HTTPException(
                    status_code=404,
                    detail="Usuario no encontrado"
                )

            cursor.execute(
                """
                SELECT id_medicamento
                FROM medicamentos
                WHERE id_medicamento = %s;
                """,
                (consumo.id_medicamento,)
            )

            if cursor.fetchone() is None:
                raise HTTPException(
                    status_code=404,
                    detail="Medicamento no encontrado"
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
                (
                    consumo.id_usuario,
                    consumo.id_medicamento
                )
            )

            lotes = cursor.fetchall()

            if not lotes:
                raise HTTPException(
                    status_code=400,
                    detail="No hay existencias disponibles de este medicamento"
                )

            unidades = {lote[4] for lote in lotes}

            if len(unidades) > 1:
                raise HTTPException(
                    status_code=400,
                    detail="Los lotes tienen unidades de contenido incompatibles"
                )

            unidad_contenido = lotes[0][4]

            existencia_total = sum(
                lote[3] for lote in lotes
            )
            cantidad_consumir=Decimal(str(consumo.cantidad))

            if existencia_total < cantidad_consumir:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        f"Existencias insuficientes. "
                        f"Disponible: {existencia_total} {unidad_contenido}"
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
                    (
                        nuevo_contenido,
                        id_inventario
                    )
                )

                lotes_utilizados.append({
                    "id_inventario": id_inventario,
                    "lote": numero_lote,
                    "cantidad_descontada": cantidad_descontar,
                    "contenido_restante": nuevo_contenido
                })

                cantidad_restante -= cantidad_descontar

            conexion.commit()

            return {
                "mensaje": "Consumo registrado correctamente",
                "id_medicamento": consumo.id_medicamento,
                "cantidad_consumida": consumo.cantidad,
                "unidad_contenido": unidad_contenido,
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

