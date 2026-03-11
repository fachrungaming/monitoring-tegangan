import paho.mqtt.client as mqtt
import sqlite3
import json
import os

# MQTT Configuration
MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT = 1883
MQTT_TOPIC = "elban/upg/sensor_data_unique_3c5d"
DB_NAME = "voltage_monitor.db"

def save_to_db(data):
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('''
        INSERT INTO sensor_history (voltage, current, power, energy, frequency, pf)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            data.get('voltage'),
            data.get('current'),
            data.get('power'),
            data.get('energy'),
            data.get('frequency'),
            data.get('pf')
        ))
        conn.commit()
        conn.close()
        print(f"Saved: V={data.get('voltage')} I={data.get('current')} P={data.get('power')}")
    except Exception as e:
        print(f"Database error: {e}")

def on_connect(client, userdata, flags, rc):
    print(f"Connected to MQTT Broker with result code {rc}")
    client.subscribe(MQTT_TOPIC)

def on_message(client, userdata, msg):
    try:
        payload = msg.payload.decode()
        data = json.loads(payload)
        save_to_db(data)
    except Exception as e:
        print(f"Error processing message: {e}")

def main():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    print("Starting MQTT Link to SQLite...")
    try:
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        client.loop_forever()
    except Exception as e:
        print(f"Connection error: {e}")

if __name__ == "__main__":
    main()
