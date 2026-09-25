from fastapi import APIRouter
from database import obtener_conexion

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
