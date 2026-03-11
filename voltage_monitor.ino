/*
  ESP32 Voltage Monitor with PZEM-004T v3.0
*/

#include <WiFi.h>
#include <PubSubClient.h>
#include <PZEM004Tv30.h>
#include <ArduinoJson.h>

// --- Konfigurasi WiFi ---
const char* ssid = "Tidak";       // GANTI DENGAN NAMA WIFI ANDA
const char* password = "tidaktau"; // GANTI DENGAN PASSWORD WIFI ANDA

// --- Konfigurasi MQTT ---
const char* mqtt_server = "broker.hivemq.com";
const int mqtt_port = 1883;
const char* mqtt_topic = "elban/voltage/data";
const char* mqtt_lwt_topic = "elban/status";

// --- Hardware Pins ---
#define PZEM_RX_PIN 16
#define PZEM_TX_PIN 17
#define PZEM_SERIAL Serial2

PZEM004Tv30 pzem(PZEM_SERIAL, PZEM_RX_PIN, PZEM_TX_PIN);
WiFiClient espClient;
PubSubClient client(espClient);

unsigned long lastMsg = 0;

void setup_wifi() {
  delay(10);
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi connected");
}

void reconnect() {
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    if (client.connect("ESP32VoltageMonitor", mqtt_lwt_topic, 1, true, "offline")) {
      Serial.println("connected");
      client.publish(mqtt_lwt_topic, "online", true);
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      delay(5000);
    }
  }
}

void setup() {
  Serial.begin(115200);
  setup_wifi();
  client.setServer(mqtt_server, mqtt_port);
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  unsigned long now = millis();
  if (now - lastMsg > 2000) { 
    lastMsg = now;

    float voltage = pzem.voltage();
    float current = pzem.current();
    float power = pzem.power();
    float energy = pzem.energy();
    float frequency = pzem.frequency();
    float pf = pzem.pf();

    if (isnan(voltage)) {
      Serial.println("Error reading voltage");
    } else {
      StaticJsonDocument<200> doc;
      doc["voltage"] = voltage;
      doc["current"] = current;
      doc["power"] = power;
      doc["energy"] = energy;
      doc["frequency"] = frequency;
      doc["pf"] = pf;

      char buffer[256];
      serializeJson(doc, buffer);
      client.publish(mqtt_topic, buffer);
      Serial.print("Published: ");
      Serial.println(buffer);
    }
  }
}
