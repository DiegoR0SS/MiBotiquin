
from fastapi import APIRouter, HTTPException
from database import obtener_conexion
from models.medicamento import MedicamentoCrear, MedicamentoActualizar

router = APIRouter(
    prefix="/medicamentos",
    tags=["Medicamentos"]
)


@router.get("")
def obtener_medicamentos():
    conexion = obtener_conexion()

    try:
        with conexion.cursor() as cursor:
            cursor.execute("""
                SELECT
                    id_medicamento,
                    nombre_comercial,
                    forma_farmaceutica,
                    via_administracion,
                    laboratorio,
                    descripcion
                FROM medicamentos
                ORDER BY id_medicamento;
            """)

            medicamentos = cursor.fetchall()

            resultado = []

            for medicamento in medicamentos:
                resultado.append({
                    "id_medicamento": medicamento[0],
                    "nombre_comercial": medicamento[1],
                    "forma_farmaceutica": medicamento[2],
                    "via_administracion": medicamento[3],
                    "laboratorio": medicamento[4],
                    "descripcion": medicamento[5]
                })

            return resultado

    finally:
        conexion.close()

@router.post("")
def crear_medicamento(medicamento: MedicamentoCrear):
    conexion = obtener_conexion()

    try:
        with conexion.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO medicamentos (
                    nombre_comercial,
                    forma_farmaceutica,
                    via_administracion,
                    laboratorio,
                    descripcion
                )
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id_medicamento;
                """,
                (
                    medicamento.nombre_comercial,
                    medicamento.forma_farmaceutica,
                    medicamento.via_administracion,
                    medicamento.laboratorio,
                    medicamento.descripcion
                )
            )

            id_medicamento = cursor.fetchone()[0]

            conexion.commit()

            return {
                "mensaje": "Medicamento registrado correctamente",
                "id_medicamento": id_medicamento
            }

    except Exception:
        conexion.rollback()
        raise

    finally:
        conexion.close()

@router.get("/{id_medicamento}")
def obtener_medicamento(id_medicamento: int):
    conexion = obtener_conexion()

    try:
        with conexion.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    id_medicamento,
                    nombre_comercial,
                    forma_farmaceutica,
                    via_administracion,
                    laboratorio,
                    descripcion
                FROM medicamentos
                WHERE id_medicamento = %s;
                """,
                (id_medicamento,)
            )

            medicamento = cursor.fetchone()

            if medicamento is None:
                raise HTTPException(
                    status_code=404,
                    detail="Medicamento no encontrado"
                )

            return {
                "id_medicamento": medicamento[0],
                "nombre_comercial": medicamento[1],
                "forma_farmaceutica": medicamento[2],
                "via_administracion": medicamento[3],
                "laboratorio": medicamento[4],
                "descripcion": medicamento[5]
            }

    finally:
        conexion.close()

@router.put("/{id_medicamento}")
def actualizar_medicamento(
    id_medicamento: int,
    medicamento: MedicamentoActualizar
):
    conexion = obtener_conexion()

    try:
        with conexion.cursor() as cursor:
            cursor.execute(
                """
                UPDATE medicamentos
                SET
                    nombre_comercial = %s,
                    forma_farmaceutica = %s,
                    via_administracion = %s,
                    laboratorio = %s,
                    descripcion = %s
                WHERE id_medicamento = %s
                RETURNING id_medicamento;
                """,
                (
                    medicamento.nombre_comercial,
                    medicamento.forma_farmaceutica,
                    medicamento.via_administracion,
                    medicamento.laboratorio,
                    medicamento.descripcion,
                    id_medicamento
                )
            )

            resultado = cursor.fetchone()

            if resultado is None:
                conexion.rollback()

                raise HTTPException(
                    status_code=404,
                    detail="Medicamento no encontrado"
                )

            conexion.commit()

            return {
                "mensaje": "Medicamento actualizado correctamente",
                "id_medicamento": resultado[0]
            }

    except HTTPException:
        raise

    except Exception:
        conexion.rollback()
        raise

    finally:
        conexion.close()

@router.delete("/{id_medicamento}")
def eliminar_medicamento(id_medicamento: int):
    conexion = obtener_conexion()

    try:
        with conexion.cursor() as cursor:
            cursor.execute(
                """
                DELETE FROM medicamentos
                WHERE id_medicamento = %s
                RETURNING id_medicamento;
                """,
                (id_medicamento,)
            )

            resultado = cursor.fetchone()

            if resultado is None:
                conexion.rollback()

                raise HTTPException(
                    status_code=404,
                    detail="Medicamento no encontrado"
                )

            conexion.commit()

            return {
                "mensaje": "Medicamento eliminado correctamente"
            }

    except HTTPException:
        raise

    except Exception:
        conexion.rollback()
        raise

    finally:
        conexion.close()
