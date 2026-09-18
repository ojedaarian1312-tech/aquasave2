/*
 * AQUASAVE - NodeMCU ESP8266
 * Mide con HC-SR04, indica el estado con LEDs/buzzer y publica JSON por HTTP.
 * Instale la librería NewPing desde el Library Manager de Arduino IDE.
 */
#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <WiFiClient.h>
#include <NewPing.h>

// --- Personalice estas cuatro constantes para cada prototipo ---
const char* WIFI_SSID = "TU_RED_WIFI";
const char* WIFI_PASSWORD = "TU_CLAVE_WIFI";
const char* SERVER_URL = "http://192.168.1.50:8000/api/mediciones"; // IP LAN, nunca localhost
const char* DEVICE_ID = "AQ-001"; // Debe existir previamente en la API

// Pines NodeMCU (los nombres D corresponden a las etiquetas de la placa).
const byte TRIGGER_PIN = D1;
const byte ECHO_PIN = D2; // El ECHO del HC-SR04 necesita divisor 5V a 3.3V.
const byte LED_VERDE = D5;
const byte LED_AMARILLO = D6;
const byte LED_ROJO = D7;
const byte BUZZER = D8;
const unsigned int MAX_DISTANCIA_CM = 400;
const unsigned long INTERVALO_MS = 30000;

// Una distancia menor indica más agua: adapte los umbrales a la altura del tanque.
const float DISTANCIA_ALTO_CM = 15.0;
const float DISTANCIA_MEDIO_CM = 45.0;
NewPing sonar(TRIGGER_PIN, ECHO_PIN, MAX_DISTANCIA_CM);
unsigned long ultimaMedicion = 0;

enum Nivel { BAJO, MEDIO, ALTO };

void conectarWifi() {
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  Serial.print("Conectando WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print('.');
  }
  Serial.println(" conectado: " + WiFi.localIP().toString());
}

Nivel calcularNivel(float distancia) {
  if (distancia <= DISTANCIA_ALTO_CM) return ALTO;
  if (distancia <= DISTANCIA_MEDIO_CM) return MEDIO;
  return BAJO;
}

const char* textoNivel(Nivel nivel) {
  if (nivel == ALTO) return "ALTO";
  if (nivel == MEDIO) return "MEDIO";
  return "BAJO";
}

void apagarLeds() {
  digitalWrite(LED_VERDE, LOW);
  digitalWrite(LED_AMARILLO, LOW);
  digitalWrite(LED_ROJO, LOW);
}

void indicarNivel(Nivel nivel) {
  apagarLeds();
  // Patrones audibles: bajo=1 beep, medio=2, alto=3 beeps rápidos.
  byte cantidad = nivel == BAJO ? 1 : (nivel == MEDIO ? 2 : 3);
  byte led = nivel == BAJO ? LED_VERDE : (nivel == MEDIO ? LED_AMARILLO : LED_ROJO);
  digitalWrite(led, HIGH);
  for (byte i = 0; i < cantidad; i++) {
    tone(BUZZER, nivel == ALTO ? 1400 : 900, 120);
    delay(200);
  }
  noTone(BUZZER);
}

void enviarMedicion(float distancia, Nivel nivel) {
  if (WiFi.status() != WL_CONNECTED) conectarWifi();
  WiFiClient cliente;
  HTTPClient http;
  if (!http.begin(cliente, SERVER_URL)) {
    Serial.println("URL de servidor inválida");
    return;
  }
  http.addHeader("Content-Type", "application/json");
  String json = "{\"dispositivo_id\":\"" + String(DEVICE_ID) +
                "\",\"nivel\":\"" + textoNivel(nivel) +
                "\",\"distancia\":" + String(distancia, 1) + "}";
  int codigo = http.POST(json);
  Serial.printf("POST %d: %s\n", codigo, json.c_str());
  http.end();
}

void setup() {
  Serial.begin(115200);
  pinMode(LED_VERDE, OUTPUT); pinMode(LED_AMARILLO, OUTPUT);
  pinMode(LED_ROJO, OUTPUT); pinMode(BUZZER, OUTPUT);
  apagarLeds();
  conectarWifi();
}

void loop() {
  if (millis() - ultimaMedicion < INTERVALO_MS) return;
  ultimaMedicion = millis();
  delay(50); // Estabiliza la lectura ultrasónica.
  unsigned int cm = sonar.ping_cm();
  if (cm == 0) { // NewPing devuelve 0 si no hubo eco dentro del rango máximo.
    Serial.println("Lectura HC-SR04 no disponible; no se envía dato.");
    return;
  }
  Nivel nivel = calcularNivel((float)cm);
  indicarNivel(nivel);
  enviarMedicion((float)cm, nivel);
}
