from datetime import date, time
from pydantic import BaseModel, Field


class MedicamentoTratamientoCrear(BaseModel):
    id_medicamento: int
    cantidad_dosis: float = Field(gt=0)
    unidad_dosis: str
    frecuencia: str
    duracion_dias: int | None = Field(default=None, gt=0)
    indicaciones: str | None = None
    horarios: list[time]


class TratamientoCrear(BaseModel):
    id_usuario: int
    nombre: str
    fecha_inicio: date
    fecha_fin: date | None = None
    indicaciones: str | None = None
    medicamentos: list[MedicamentoTratamientoCrear]
