from pydantic import BaseModel

class PrincipioActivoMedicamento(BaseModel):
    nombre: str
    concentracion: str

class MedicamentoCrear(BaseModel):
    nombre_comercial: str
    forma_farmaceutica: str
    via_administracion: str
    laboratorio: str | None = None
    descripcion: str | None = None
    principios_activos: list[PrincipioActivoMedicamento]

class MedicamentoActualizar(BaseModel):
    nombre_comercial: str
    forma_farmaceutica: str
    via_administracion: str
    laboratorio: str | None = None
    descripcion: str | None = None
    principios_activos: list[PrincipioActivoMedicamento]
