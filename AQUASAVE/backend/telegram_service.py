"""Integración aislada con Telegram para que no afecte el registro de datos."""
from datetime import datetime
import httpx
from .config import settings


async def enviar_alerta_alto(nombre: str, distancia: float, fecha: datetime) -> bool:
    """Envía la alerta y devuelve False ante errores sin propagar secretos."""
    if not settings.telegram_bot_token or not settings.telegram_chat_id:
        return False
    texto = (f"🚨 AQUASAVE: nivel ALTO\n"
             f"Dispositivo: {nombre}\nNivel: ALTO\n"
             f"Distancia: {distancia:.1f} cm\nHora: {fecha.isoformat()}")
    url = f"https://api.telegram.org/bot{settings.telegram_bot_token}/sendMessage"
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(url, json={"chat_id": settings.telegram_chat_id, "text": texto})
            response.raise_for_status()
        return True
    except httpx.HTTPError:
        return False
