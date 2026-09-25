from fastapi import FastAPI
from database import obtener_conexion

app = FastAPI(
    title="Mi Botiquín API",
    description="API para la administración y control de medicamentos en el hogar",
    version="1.0.0"
)


@app.get("/")
def inicio():
    return {
        "mensaje": "API de Mi Botiquín funcionando correctamente"
    }


@app.get("/medicamentos")
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
