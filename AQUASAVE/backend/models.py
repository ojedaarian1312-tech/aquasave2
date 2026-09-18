"""Entidades persistentes de AQUASAVE, declaradas solamente con ORM."""
from datetime import datetime, timezone
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .database import Base


class Dispositivo(Base):
    __tablename__ = "dispositivos"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    latitud: Mapped[float] = mapped_column(Float, nullable=False)
    longitud: Mapped[float] = mapped_column(Float, nullable=False)
    ubicacion: Mapped[str] = mapped_column(String(200), default="")
    activo: Mapped[bool] = mapped_column(Boolean, default=True)
    mediciones: Mapped[list["Medicion"]] = relationship(back_populates="dispositivo", cascade="all, delete-orphan")


class Medicion(Base):
    __tablename__ = "mediciones"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    dispositivo_id: Mapped[str] = mapped_column(ForeignKey("dispositivos.id"), index=True)
    nivel: Mapped[str] = mapped_column(String(10), nullable=False)
    distancia: Mapped[float] = mapped_column(Float, nullable=False)
    fecha_hora: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    dispositivo: Mapped[Dispositivo] = relationship(back_populates="mediciones")
