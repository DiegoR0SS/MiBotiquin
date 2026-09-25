from fastapi import FastAPI
from routers import medicamentos

app = FastAPI(
    title="Mi Botiquín API",
    description="API para la administración y control de medicamentos en el hogar",
    version="1.0.0"
)


app.include_router(medicamentos.router)


@app.get("/")
def inicio():
    return {
        "mensaje": "API de Mi Botiquín funcionando correctamente"
    }
