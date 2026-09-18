"""Configuración centralizada mediante variables de entorno, sin dependencias extra."""
import os
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent


def cargar_env() -> None:
    """Carga un .env simple sin sobrescribir variables ya definidas por el sistema."""
    archivo = ROOT_DIR / "backend" / ".env"
    if not archivo.exists():
        return
    for linea in archivo.read_text(encoding="utf-8").splitlines():
        if "=" in linea and not linea.lstrip().startswith("#"):
            clave, valor = linea.split("=", 1)
            os.environ.setdefault(clave.strip(), valor.strip().strip('"'))


cargar_env()


class Settings:
    """Valores de ejecución; las credenciales quedan fuera del código fuente."""

    database_url = os.getenv("DATABASE_URL", f"sqlite:///{(ROOT_DIR / 'database' / 'aquasave.db').as_posix()}")
    telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "")
    telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID", "")


settings = Settings()
