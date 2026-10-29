"""Bridge: MQTT -> REST API (Hono)  (ข้อ 6-7 ของ assignment)

ทำ 3 อย่าง
  1. pi/sensor/<type>              (ค่าตัวเลขธรรมดา)  -> POST /api/v1/sensors
  2. lora/<node>/data              (JSON)            -> POST /api/v1/sensors
  3. application/+/device/+/event/up (Chirpstack v4) -> แกะ object แล้ว republish เป็น lora/<node>/data

รัน:  python mqtt_to_api.py
env : MQTT_BROKER, MQTT_PORT, API_URL, API_SECRET
"""
import json
import os

import paho.mqtt.client as mqtt
import requests

MQTT_BROKER = os.getenv("MQTT_BROKER", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
API_URL = os.getenv("API_URL", "http://localhost:3000/api/v1")
API_SECRET = os.getenv("API_SECRET", "")

UNITS = {"temperature": "C", "humidity": "%", "distance": "cm"}


def post_reading(name: str, sensor_type: str, value: float):
    body = {
        "sensorName": name,
        "sensorType": sensor_type,
        "value": float(value),
        "unit": UNITS.get(sensor_type),
    }
    try:
        r = requests.post(
            f"{API_URL}/sensors",
            json=body,
            headers={"Authorization": f"Bearer {API_SECRET}"},
            timeout=5,
        )
        print(f"[API] {r.status_code} {body}")
    except requests.RequestException as exc:
        print(f"[API] error: {exc}")


def on_connect(client, userdata, flags, reason_code, properties):
    client.subscribe([("pi/sensor/+", 0), ("lora/+/data", 0), ("application/+/device/+/event/up", 0)])
    print("Bridge connected")


def on_message(client, userdata, msg):
    parts = msg.topic.split("/")
    payload = msg.payload.decode("utf-8", errors="replace")
    try:
        if parts[0] == "pi" and parts[1] == "sensor":
            post_reading("pi", parts[2], float(payload))

        elif parts[0] == "lora" and parts[2] == "data":
            data = json.loads(payload)
            for key in ("temperature", "humidity"):
                if key in data:
                    post_reading(parts[1], key, data[key])

        elif parts[0] == "application" and parts[-1] == "up":
            event = json.loads(payload)
            obj = event.get("object")
            if obj:
                node = event.get("deviceInfo", {}).get("deviceName", parts[3])
                client.publish(f"lora/{node}/data", json.dumps(obj), qos=1)
    except (ValueError, KeyError, IndexError) as exc:
        print(f"[bridge] skip {msg.topic}: {exc}")


client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="iot-bridge")
client.on_connect = on_connect
client.on_message = on_message
client.connect(MQTT_BROKER, MQTT_PORT, 60)
client.loop_forever()
