import paho.mqtt.client as mqtt
import json
import time
import random

# MQTT Configuration (Same as ESP32 and code.html)
MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT = 1883
MQTT_TOPIC_DATA = "elban/upg/sensor_data_unique_3c5d"
MQTT_TOPIC_STATUS = "elban/upg/status_unique_3c5d"

client = mqtt.Client()

print(f"Connecting to MQTT Broker: {MQTT_BROKER}...")
try:
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
except Exception as e:
    print(f"Error connecting: {e}")
    exit()

# Set status to online
client.publish(MQTT_TOPIC_STATUS, "online", retain=True)
print("Status set to ONLINE")

try:
    while True:
        # Generate random realistic voltage data
        voltage = round(random.uniform(215.0, 225.0), 1)
        # Occasionally simulate a drop or surge
        if random.random() < 0.1:
            voltage = round(random.uniform(190.0, 250.0), 1)
            
        frequency = round(random.uniform(49.9, 50.1), 2)
        
        data = {
            "voltage": voltage,
            "current": round(random.uniform(0.5, 2.5), 2),
            "power": round(voltage * 1.5, 1),
            "energy": round(random.uniform(10.0, 20.0), 2),
            "frequency": frequency,
            "pf": 0.95
        }
        
        payload = json.dumps(data)
        client.publish(MQTT_TOPIC_DATA, payload)
        print(f"Published Simulation Data: {payload}")
        
        time.sleep(2) # Send every 2 seconds

except KeyboardInterrupt:
    print("\nStopping simulation...")
    client.publish(MQTT_TOPIC_STATUS, "offline", retain=True)
    client.disconnect()
