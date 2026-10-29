"""MCP Server บน Raspberry Pi (ต่อยอดจาก week12/server.py)

Tool ทั้ง 4 ตามโจทย์:
  1. read_pi_sensors      อ่านเซนเซอร์บนบอร์ดโดยตรง (SHT31, Ultrasonic, สถานะ LED)
  2. control_pi_device    สั่งอุปกรณ์บน Pi (LED)
  3. read_from_mqtt       อ่านค่าล่าสุดจาก MQTT (รวมถึงข้อมูลจาก LoRa node)
  4. publish_to_mqtt      ส่งค่าเข้า MQTT (จำกัดเฉพาะ topic ใน whitelist)

รัน:  python mcp_server.py        (เปิดที่ http://0.0.0.0:8000/mcp)
"""
import json
import logging
import os
import threading
import time

import paho.mqtt.client as mqtt
from mcp.server import MCPServer
from mcp.server.transport_security import TransportSecuritySettings

import config
import sensors

logging.basicConfig(level=logging.INFO)
sensors.init_gpio()

# ---------------------------------------------------------------- MQTT
latest = {}                 # topic -> {"value": str, "time": epoch}
latest_lock = threading.Lock()
led_state = "OFF"


def apply_led(action: str) -> str:
    """เปิด/ปิด LED จริง แล้วประกาศสถานะที่ topic .../state"""
    global led_state
    led_state = "ON" if action.upper() == "ON" else "OFF"
    sensors.set_led(led_state == "ON")
    mqtt_client.publish(config.TOPIC_LED_STATE, led_state, qos=1, retain=True)
    return led_state


def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        client.subscribe([("pi/#", 0), ("lora/#", 0)])
        logging.info("MQTT connected")


def on_message(client, userdata, msg):
    payload = msg.payload.decode("utf-8", errors="replace")
    with latest_lock:
        latest[msg.topic] = {"value": payload, "time": time.time()}
    # คำสั่งจาก Dashboard (หรือใครก็ตามที่ publish มาที่ pi/device/led)
    if msg.topic == config.TOPIC_LED_CMD and payload.upper() in ("ON", "OFF"):
        apply_led(payload)


mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="pi-mcp-server")
if config.MQTT_USER:
    mqtt_client.username_pw_set(config.MQTT_USER, config.MQTT_PASS)
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.connect(config.MQTT_BROKER, config.MQTT_PORT, 60)
mqtt_client.loop_start()

# ---------------------------------------------------------------- MCP
mcp = MCPServer("RaspberryPi-IoT")


@mcp.tool()
def read_pi_sensors() -> str:
    """Read the sensors attached to the Raspberry Pi right now:
    temperature (C), humidity (%RH), distance from the ultrasonic sensor (cm)
    and the current LED state."""
    data = sensors.read_all()
    data["led"] = led_state
    return json.dumps(data, ensure_ascii=False)


@mcp.tool()
def control_pi_device(device: str, action: str) -> str:
    """Control a device on the Raspberry Pi.
    device: currently only 'led'. action: 'on' or 'off'."""
    if device.strip().lower() != "led":
        return "Error: unknown device. Supported devices: led"
    if action.strip().lower() not in ("on", "off"):
        return "Error: action must be 'on' or 'off'"
    return f"LED is {apply_led(action)}"


@mcp.tool()
def read_from_mqtt(topic: str = "") -> str:
    """Read the latest value seen on an MQTT topic, e.g. 'pi/sensor/humidity',
    'lora/node1/data'. Leave topic empty to list every topic seen so far
    with its latest value."""
    with latest_lock:
        if not topic:
            if not latest:
                return "No MQTT messages received yet."
            return json.dumps(
                {t: v["value"] for t, v in sorted(latest.items())}, ensure_ascii=False
            )
        item = latest.get(topic)
    if item is None:
        return f"No message received yet on '{topic}'."
    age = int(time.time() - item["time"])
    return json.dumps({"topic": topic, "value": item["value"], "age_seconds": age})


@mcp.tool()
def publish_to_mqtt(topic: str, payload: str) -> str:
    """Publish a message to an MQTT topic. Only whitelisted topics are allowed."""
    if topic not in config.PUBLISH_WHITELIST:
        return f"Error: topic not allowed. Allowed: {sorted(config.PUBLISH_WHITELIST)}"
    info = mqtt_client.publish(topic, payload, qos=1)
    info.wait_for_publish(timeout=5)
    if info.rc != mqtt.MQTT_ERR_SUCCESS:
        return "MQTT publish failed"
    return f"Published '{payload}' to {topic}"


if __name__ == "__main__":
    # ใส่ host ของ tunnel ใน env เช่น TUNNEL_HOST=abc123.tunnl.gg
    tunnel = os.getenv("TUNNEL_HOST", "")
    hosts = ["localhost:8000", "127.0.0.1:8000", "0.0.0.0:8000"]
    origins = []
    if tunnel:
        hosts += [tunnel, f"{tunnel}:*"]
        origins += [f"https://{tunnel}", f"https://{tunnel}/"]

    security = TransportSecuritySettings(allowed_hosts=hosts, allowed_origins=origins)
    try:
        mcp.run(transport="streamable-http", transport_security=security, host="0.0.0.0")
    finally:
        sensors.cleanup()
