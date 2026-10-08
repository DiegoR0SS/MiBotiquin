from datetime import datetime
from pydantic import BaseModel


class TomaCrear(BaseModel):
    id_horario: int
    fecha_programada: datetime


class TomaConfirmar(BaseModel):
    observaciones: str | None = None
