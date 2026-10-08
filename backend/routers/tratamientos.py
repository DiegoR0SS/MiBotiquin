from fastapi import APIRouter, HTTPException
from database import obtener_conexion
from models.tratamiento import TratamientoCrear

router = APIRouter(
    prefix="/tratamientos",
    tags=["Tratamientos"]
)


@router.post("")
def crear_tratamiento(tratamiento: TratamientoCrear):
    conexion = obtener_conexion()

    try:
        with conexion.cursor() as cursor:

            cursor.execute(
                """
                SELECT id_usuario
                FROM usuarios
                WHERE id_usuario = %s;
                """,
                (tratamiento.id_usuario,)
            )

            if cursor.fetchone() is None:
                raise HTTPException(
                    status_code=404,
                    detail="Usuario no encontrado"
                )

            if (
                tratamiento.fecha_fin is not None
                and tratamiento.fecha_fin < tratamiento.fecha_inicio
            ):
                raise HTTPException(
                    status_code=400,
                    detail="La fecha de fin no puede ser anterior a la fecha de inicio"
                )

            cursor.execute(
                """
                INSERT INTO tratamientos (
                    id_usuario,
                    nombre,
                    fecha_inicio,
                    fecha_fin,
                    indicaciones
                )
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id_tratamiento;
                """,
                (
                    tratamiento.id_usuario,
                    tratamiento.nombre,
                    tratamiento.fecha_inicio,
                    tratamiento.fecha_fin,
                    tratamiento.indicaciones
                )
            )

            id_tratamiento = cursor.fetchone()[0]

            medicamentos_creados = []

            for medicamento in tratamiento.medicamentos:

                cursor.execute(
                    """
                    SELECT id_medicamento
                    FROM medicamentos
                    WHERE id_medicamento = %s;
                    """,
                    (medicamento.id_medicamento,)
                )

                if cursor.fetchone() is None:
                    raise HTTPException(
                        status_code=404,
                        detail=(
                            f"Medicamento {medicamento.id_medicamento} "
                            f"no encontrado"
                        )
                    )

                cursor.execute(
                    """
                    INSERT INTO tratamiento_medicamentos (
                        id_tratamiento,
                        id_medicamento,
                        cantidad_dosis,
                        unidad_dosis,
                        frecuencia,
                        duracion_dias,
                        indicaciones
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    RETURNING id_tratamiento_medicamento;
                    """,
                    (
                        id_tratamiento,
                        medicamento.id_medicamento,
                        medicamento.cantidad_dosis,
                        medicamento.unidad_dosis,
                        medicamento.frecuencia,
                        medicamento.duracion_dias,
                        medicamento.indicaciones
                    )
                )

                id_tm = cursor.fetchone()[0]

                for horario in medicamento.horarios:
                    cursor.execute(
                        """
                        INSERT INTO horarios_toma (
                            id_tratamiento_medicamento,
                            hora
                        )
                        VALUES (%s, %s);
                        """,
                        (
                            id_tm,
                            horario
                        )
                    )

                medicamentos_creados.append({
                    "id_tratamiento_medicamento": id_tm,
                    "id_medicamento": medicamento.id_medicamento
                })

            conexion.commit()

            return {
                "mensaje": "Tratamiento creado correctamente",
                "id_tratamiento": id_tratamiento,
                "medicamentos": medicamentos_creados
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
def obtener_tratamientos_usuario(id_usuario: int):
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
                    id_tratamiento,
                    nombre,
                    fecha_inicio,
                    fecha_fin,
                    indicaciones
                FROM tratamientos
                WHERE id_usuario = %s
                ORDER BY fecha_inicio DESC, id_tratamiento DESC;
                """,
                (id_usuario,)
            )

            registros = cursor.fetchall()
            tratamientos = []

            for registro in registros:
                tratamientos.append({
                    "id_tratamiento": registro[0],
                    "nombre": registro[1],
                    "fecha_inicio": registro[2],
                    "fecha_fin": registro[3],
                    "indicaciones": registro[4]
                })

            return tratamientos

    finally:
        conexion.close()

@router.get("/{id_tratamiento}")
def obtener_tratamiento(id_tratamiento: int):
    conexion = obtener_conexion()

    try:
        with conexion.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    id_tratamiento,
                    id_usuario,
                    nombre,
                    fecha_inicio,
                    fecha_fin,
                    indicaciones
                FROM tratamientos
                WHERE id_tratamiento = %s;
                """,
                (id_tratamiento,)
            )

            registro = cursor.fetchone()

            if registro is None:
                raise HTTPException(
                    status_code=404,
                    detail="Tratamiento no encontrado"
                )

            tratamiento = {
                "id_tratamiento": registro[0],
                "id_usuario": registro[1],
                "nombre": registro[2],
                "fecha_inicio": registro[3],
                "fecha_fin": registro[4],
                "indicaciones": registro[5],
                "medicamentos": []
            }

            cursor.execute(
                """
                SELECT
                    tm.id_tratamiento_medicamento,
                    tm.id_medicamento,
                    m.nombre_comercial,
                    tm.cantidad_dosis,
                    tm.unidad_dosis,
                    tm.frecuencia,
                    tm.duracion_dias,
                    tm.indicaciones
                FROM tratamiento_medicamentos tm
                JOIN medicamentos m
                    ON m.id_medicamento = tm.id_medicamento
                WHERE tm.id_tratamiento = %s
                ORDER BY tm.id_tratamiento_medicamento;
                """,
                (id_tratamiento,)
            )

            medicamentos = cursor.fetchall()

            for medicamento in medicamentos:
                id_tm = medicamento[0]

                cursor.execute(
                    """
                    SELECT hora
                    FROM horarios_toma
                    WHERE id_tratamiento_medicamento = %s
                    ORDER BY hora;
                    """,
                    (id_tm,)
                )

                horarios = [
                    str(horario[0])
                    for horario in cursor.fetchall()
                ]

                tratamiento["medicamentos"].append({
                    "id_tratamiento_medicamento": id_tm,
                    "id_medicamento": medicamento[1],
                    "nombre_comercial": medicamento[2],
                    "cantidad_dosis": medicamento[3],
                    "unidad_dosis": medicamento[4],
                    "frecuencia": medicamento[5],
                    "duracion_dias": medicamento[6],
                    "indicaciones": medicamento[7],
                    "horarios": horarios
                })

            return tratamiento

    finally:
        conexion.close()
