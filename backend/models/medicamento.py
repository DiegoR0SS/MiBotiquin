from pydantic import BaseModel


class MedicamentoCrear(BaseModel):
    nombre_comercial: str
    forma_farmaceutica: str
    via_administracion: str
    laboratorio: str | None = None
    descripcion: str | None = None

class MedicamentoActualizar(BaseModel):
    nombre_comercial: str
    forma_farmaceutica: str
    via_administracion: str
    laboratorio: str | None = None
    descripcion: str | None = None
