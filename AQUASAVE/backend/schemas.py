"""Contratos de entrada y salida de la API."""
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, ConfigDict, Field


class NivelAgua(str, Enum):
    BAJO = "BAJO"
    MEDIO = "MEDIO"
    ALTO = "ALTO"


class DispositivoCrear(BaseModel):
    id: str = Field(min_length=1, max_length=64)
    nombre: str = Field(min_length=1, max_length=100)
    latitud: float = Field(ge=-90, le=90)
    longitud: float = Field(ge=-180, le=180)
    ubicacion: str = Field(default="", max_length=200)
    activo: bool = True


class DispositivoSalida(DispositivoCrear):
    model_config = ConfigDict(from_attributes=True)
    ultima_medicion: "MedicionSalida | None" = None


class MedicionCrear(BaseModel):
    dispositivo_id: str = Field(min_length=1, max_length=64)
    nivel: NivelAgua
    distancia: float = Field(ge=0, le=1000)


class MedicionSalida(MedicionCrear):
    id: int
    fecha_hora: datetime
    model_config = ConfigDict(from_attributes=True)
