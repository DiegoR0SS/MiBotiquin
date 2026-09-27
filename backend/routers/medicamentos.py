
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
                ORDER BY id_medicamento;
                """
            )

            medicamentos = cursor.fetchall()

            resultado = []

            for medicamento in medicamentos:
                id_medicamento = medicamento[0]

                cursor.execute(
                    """
                    SELECT
                        pa.id_principio_activo,
                        pa.nombre,
                        mpa.concentracion
                    FROM medicamento_principio_activo mpa
                    JOIN principios_activos pa
                        ON pa.id_principio_activo = mpa.id_principio_activo
                    WHERE mpa.id_medicamento = %s
                    ORDER BY pa.nombre;
                    """,
                    (id_medicamento,)
                )

                principios = cursor.fetchall()

                resultado.append({
                    "id_medicamento": medicamento[0],
                    "nombre_comercial": medicamento[1],
                    "forma_farmaceutica": medicamento[2],
                    "via_administracion": medicamento[3],
                    "laboratorio": medicamento[4],
                    "descripcion": medicamento[5],
                    "principios_activos": [
                        {
                            "id_principio_activo": principio[0],
                            "nombre": principio[1],
                            "concentracion": principio[2]
                        }
                        for principio in principios
                    ]
                })

            return resultado

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

            cursor.execute(
                """
                SELECT
                    pa.id_principio_activo,
                    pa.nombre,
                    mpa.concentracion
                FROM medicamento_principio_activo mpa
                JOIN principios_activos pa
                    ON pa.id_principio_activo = mpa.id_principio_activo
                WHERE mpa.id_medicamento = %s
                ORDER BY pa.nombre;
                """,
                (id_medicamento,)
            )

            principios = cursor.fetchall()

            return {
                "id_medicamento": medicamento[0],
                "nombre_comercial": medicamento[1],
                "forma_farmaceutica": medicamento[2],
                "via_administracion": medicamento[3],
                "laboratorio": medicamento[4],
                "descripcion": medicamento[5],
                "principios_activos": [
                    {
                        "id_principio_activo": principio[0],
                        "nombre": principio[1],
                        "concentracion": principio[2]
                    }
                    for principio in principios
                ]
            }

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

            for principio in medicamento.principios_activos:

                cursor.execute(
                    """
                    SELECT id_principio_activo
                    FROM principios_activos
                    WHERE LOWER(nombre) = LOWER(%s);
                    """,
                    (principio.nombre,)
                )

                resultado = cursor.fetchone()

                if resultado is None:
                    cursor.execute(
                        """
                        INSERT INTO principios_activos (nombre)
                        VALUES (%s)
                        RETURNING id_principio_activo;
                        """,
                        (principio.nombre,)
                    )

                    id_principio_activo = cursor.fetchone()[0]

                else:
                    id_principio_activo = resultado[0]

                cursor.execute(
                    """
                    INSERT INTO medicamento_principio_activo (
                        id_medicamento,
                        id_principio_activo,
                        concentracion
                    )
                    VALUES (%s, %s, %s);
                    """,
                    (
                        id_medicamento,
                        id_principio_activo,
                        principio.concentracion
                    )
                )

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

            cursor.execute(
                """
                DELETE FROM medicamento_principio_activo
                WHERE id_medicamento = %s;
                """,
                (id_medicamento,)
            )

            for principio in medicamento.principios_activos:
                cursor.execute(
                    """
                    SELECT id_principio_activo
                    FROM principios_activos
                    WHERE LOWER(nombre) = LOWER(%s);
                    """,
                    (principio.nombre,)
                )

                resultado_principio = cursor.fetchone()

                if resultado_principio is None:
                    cursor.execute(
                        """
                        INSERT INTO principios_activos (nombre)
                        VALUES (%s)
                        RETURNING id_principio_activo;
                        """,
                        (principio.nombre,)
                    )

                    id_principio_activo = cursor.fetchone()[0]

                else:
                    id_principio_activo = resultado_principio[0]

                cursor.execute(
                    """
                    INSERT INTO medicamento_principio_activo (
                        id_medicamento,
                        id_principio_activo,
                        concentracion
                    )
                    VALUES (%s, %s, %s);
                    """,
                    (
                        id_medicamento,
                        id_principio_activo,
                        principio.concentracion
                    )
                )

            conexion.commit()

            return {
                "mensaje": "Medicamento actualizado correctamente",
                "id_medicamento": id_medicamento
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
