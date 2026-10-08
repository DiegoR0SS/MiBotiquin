from fastapi import FastAPI
from routers import medicamentos, inventario, tratamientos, tomas


app = FastAPI(
    title="Mi Botiquín API",
    description="API para la administración y control de medicamentos en el hogar",
    version="1.0.0"
)


app.include_router(medicamentos.router)
app.include_router(inventario.router)
app.include_router(tratamientos.router)
app.include_router(tomas.router)

@app.get("/")
def inicio():
    return {
        "mensaje": "API de Mi Botiquín funcionando correctamente"
    }
