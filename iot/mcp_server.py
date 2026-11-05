import json
import os
import threading
import time

import paho.mqtt.client as mqtt
from gpiozero import LED, Button, DigitalOutputDevice
from mcp.server import MCPServer
from mcp.server.transport_security import TransportSecuritySettings

BROKER, PORT = "broker.hivemq.com", 1883
P = "yossaphol-iot-3502"
T_LED_CMD = f"{P}/pi/device/led"
T_LED_STATE = f"{P}/pi/device/led/state"
T_IR = f"{P}/pi/sensor/ir"

led = LED(4)                                          # pin 7
en = DigitalOutputDevice(24, initial_value=True)      # IR EN = pin 18
ir = Button(23, pull_up=True, bounce_time=0.02)       # IR OUT = pin 16 (active LOW)

latest = {}                  # topic -> (payload, เวลาที่ได้รับ)
lock = threading.Lock()

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=f"pi-mcp-{P}")


def publish_led():
    client.publish(T_LED_STATE, "ON" if led.is_lit else "OFF", qos=1, retain=True)


def publish_ir():
    client.publish(T_IR, "DETECTED" if ir.is_pressed else "CLEAR", qos=1, retain=True)


def set_led(on: bool):
    led.on() if on else led.off()
    publish_led()


def on_connect(c, userdata, flags, reason_code, properties):
    print("MQTT connected:", reason_code)
    c.subscribe(f"{P}/#", qos=1)
    publish_led()
    publish_ir()


def on_message(c, userdata, msg):
    payload = msg.payload.decode("utf-8", errors="replace").strip()
    with lock:
        latest[msg.topic] = (payload, time.time())
    if msg.topic == T_LED_CMD:
        cmd = payload.upper()
        if cmd in ("ON", "OFF"):
            set_led(cmd == "ON")
            print("LED ->", cmd, "(from MQTT)")


client.on_connect = on_connect
client.on_message = on_message
ir.when_pressed = publish_ir
ir.when_released = publish_ir

mcp = MCPServer("RaspberryPi-IoT")


def _short(full: str) -> str:
    return full[len(P) + 1:] if full.startswith(P + "/") else full


@mcp.tool()
def read_pi_sensors() -> str:
    """Read the sensors on the Raspberry Pi right now: the IR obstacle sensor
    (DETECTED or CLEAR) and the current LED state (ON or OFF)."""
    return json.dumps({
        "ir": "DETECTED" if ir.is_pressed else "CLEAR",
        "led": "ON" if led.is_lit else "OFF",
    })


@mcp.tool()
def control_pi_device(device: str, action: str) -> str:
    """Control a device on the Raspberry Pi directly via GPIO.
    device must be 'led'. action must be 'on' or 'off'."""
    if device.strip().lower() != "led":
        return "Error: only device 'led' is supported"
    a = action.strip().lower()
    if a not in ("on", "off"):
        return "Error: action must be on or off"
    set_led(a == "on")
    return f"LED is {a.upper()}"


@mcp.tool()
def read_from_mqtt(topic: str = "") -> str:
    """Read the latest message seen on the MQTT broker (HiveMQ).
    topic is relative to the project prefix. Useful topics:
    'lora/node1/data' = light sensor (LDR) on the LoRa node as JSON
    (light = percent, dark = true/false, rssi, snr),
    'pi/sensor/ir', 'pi/device/led/state'.
    Leave topic empty to list every topic seen so far."""
    topic = topic.strip().strip("/")
    with lock:
        if not topic:
            return json.dumps({_short(t): v[0] for t, v in latest.items()}, ensure_ascii=False)
        item = latest.get(f"{P}/{topic}")
    if item is None:
        return f"No message received yet on {topic}"
    payload, ts = item
    return json.dumps({"topic": topic, "payload": payload,
                       "age_seconds": round(time.time() - ts)}, ensure_ascii=False)


ALLOWED_PUBLISH = {"pi/device/led": {"ON", "OFF"}}


@mcp.tool()
def publish_to_mqtt(topic: str, payload: str) -> str:
    """Publish a message to the MQTT broker. Only one command is allowed:
    topic 'pi/device/led' with payload 'ON' or 'OFF' (turns the Pi LED on/off)."""
    topic = topic.strip().strip("/")
    payload = payload.strip().upper()
    if payload not in ALLOWED_PUBLISH.get(topic, set()):
        return "Error: only topic 'pi/device/led' with payload ON or OFF is allowed"
    info = client.publish(f"{P}/{topic}", payload, qos=1)
    info.wait_for_publish(timeout=5)
    if info.rc != mqtt.MQTT_ERR_SUCCESS:
        return "MQTT publish failed"
    return f"Published {payload} to {topic}"


if __name__ == "__main__":
    host = os.getenv("TUNNEL_HOST", "").strip()      # เช่น ruby-mountain-41a2c079.tunnl.gg
    hosts = ["localhost:8000", "127.0.0.1:8000", "0.0.0.0:8000"]
    origins = []
    if host:
        hosts += [host, f"{host}:*"]
        origins += [f"https://{host}", f"https://{host}/"]
    security = TransportSecuritySettings(allowed_hosts=hosts, allowed_origins=origins)

    client.connect(BROKER, PORT, 60)
    client.loop_start()
    try:
        mcp.run(transport="streamable-http", transport_security=security, host="0.0.0.0")
    finally:
        client.loop_stop()
        client.disconnect()