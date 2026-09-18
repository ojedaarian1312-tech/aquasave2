"""Conexión y ciclo de vida de las sesiones SQLAlchemy."""
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from .config import ROOT_DIR, settings


# Asegura que SQLite tenga un directorio antes de abrir el archivo.
(ROOT_DIR / "database").mkdir(exist_ok=True)
engine = create_engine(settings.database_url, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


class Base(DeclarativeBase):
    """Clase base para todos los modelos ORM."""


def get_db():
    """Entrega una sesión por solicitud y la cierra siempre al finalizar."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
