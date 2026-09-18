# AQUASAVE

Sistema IoT para supervisar niveles de agua con múltiples ESP8266, API FastAPI,
SQLite, alertas de Telegram y tablero web.

## Estructura

```
arduino/AQUASAVE_ESP8266/AQUASAVE_ESP8266.ino  Sketch para NodeMCU
backend/                                           API, modelos y servicios
frontend/                                          Panel web estático
database/                                          Base SQLite creada al iniciar
```

## 1. Backend

En una terminal de VS Code, desde la raíz del proyecto:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r backend\requirements.txt
Copy-Item backend\.env.example backend\.env
uvicorn backend.main:app --reload
```

Edite `backend/.env`: `TELEGRAM_BOT_TOKEN` y `TELEGRAM_CHAT_ID` son opcionales,
pero necesarios para alertas. Abra `http://127.0.0.1:8000` para el dashboard y
`http://127.0.0.1:8000/docs` para probar la API. La base se crea en
`database/aquasave.db` automáticamente.

## 2. Registrar un prototipo

Antes de enviar mediciones, cree cada dispositivo (también se puede usar Swagger):

```powershell
Invoke-RestMethod -Method Post http://127.0.0.1:8000/api/dispositivos -ContentType 'application/json' -Body '{"id":"AQ-001","nombre":"Tanque Norte","latitud":-34.6037,"longitud":-58.3816,"ubicacion":"Azotea","activo":true}'
```

## 3. Arduino IDE

1. Instale el soporte de placas **ESP8266 by ESP8266 Community** y seleccione
   **NodeMCU 1.0 (ESP-12E Module)**.
2. Instale la biblioteca **NewPing** desde el gestor de bibliotecas.
3. Abra `arduino/AQUASAVE_ESP8266/AQUASAVE_ESP8266.ino`.
4. Cambie `WIFI_SSID`, `WIFI_PASSWORD`, `SERVER_URL` (IP LAN del ordenador) y
   `DEVICE_ID`. No use `localhost`: para el ESP debe ser algo como
   `http://192.168.1.50:8000/api/mediciones`.
5. Ajuste las alturas `DISTANCIA_ALTO_CM` y `DISTANCIA_MEDIO_CM` para su tanque,
   conecte el NodeMCU y cargue el sketch.

## Cableado sugerido

| Componente | NodeMCU |
| --- | --- |
| HC-SR04 TRIG | D1 (GPIO5) |
| HC-SR04 ECHO | D2 (GPIO4), mediante divisor 5V→3.3V |
| LED verde | D5 (GPIO14), con resistencia |
| LED amarillo | D6 (GPIO12), con resistencia |
| LED rojo | D7 (GPIO13), con resistencia |
| Buzzer | D8 (GPIO15) |

El HC-SR04 requiere 5 V; **proteja el pin ECHO con un divisor de tensión** antes
de conectarlo a un GPIO de 3.3 V del ESP8266.

## API principal

- `POST /api/dispositivos`: registra un dispositivo.
- `GET /api/dispositivos`: lista dispositivos con su última medición.
- `POST /api/mediciones`: recibe `{ "dispositivo_id", "nivel", "distancia" }`.
- `GET /api/mediciones?dispositivo_id=&limit=`: historial.
- `GET /api/dispositivos/{id}/mediciones`: historial de un dispositivo.

Los niveles válidos son `BAJO`, `MEDIO` y `ALTO`. La alerta Telegram se intenta
solamente después de confirmar la medición en SQLite; un fallo de Telegram no
descarta el registro.
