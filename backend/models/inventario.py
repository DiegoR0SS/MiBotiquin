from datetime import date

from pydantic import BaseModel, Field


class InventarioCrear(BaseModel):
    id_usuario: int
    id_medicamento: int
    lote: str | None = None
    fecha_caducidad: date | None = None
    cantidad_envases: int = Field(gt=0)
    tipo_envase: str
    contenido_por_envase: float = Field(gt=0)
    unidad_contenido: str
    nivel_minimo: float = Field(ge=0)

class InventarioActualizar(BaseModel):
    lote: str | None = None
    fecha_caducidad: date | None = None
    cantidad_envases: int = Field(gt=0)
    tipo_envase: str
    contenido_por_envase: float = Field(gt=0)
    unidad_contenido: str
    nivel_minimo: float = Field(ge=0)

class EntradaInventario(BaseModel):
    cantidad_envases: int = Field(gt=0)

class ConsumoInventario(BaseModel):
    id_usuario: int
    id_medicamento: int
    cantidad: float = Field(gt=0)
