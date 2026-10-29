import os
import logging
import threading
import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO
from mcp.server import MCPServer
from mcp.server.transport_security import TransportSecuritySettings


LIGHT = 4  # GPIO4 (BCM) = physical pin 7

GPIO.setmode(GPIO.BCM)
GPIO.setup(LIGHT, GPIO.OUT, initial=GPIO.LOW)

logging.basicConfig(level=logging.INFO)

# ตั้งค่า MQTT Broker
BROKER = os.getenv("MQTT_BROKER", "mqtt-dashboard.com")
PORT = 1883

DEVICE_ID = "personlight-demo"
COMMAND_TOPIC = f"{DEVICE_ID}/command"
STATUS_TOPIC = f"{DEVICE_ID}/person"

person_status = None
status_lock = threading.Lock()

# MQTT connection
mqtt_client = mqtt.Client(
    mqtt.CallbackAPIVersion.VERSION2,
    client_id="raspi-iot-mcp-yossaphol"
)


def apply_led(action: str) -> None:
    """Drive the physical LED on GPIO4."""
    GPIO.output(LIGHT, GPIO.HIGH if action == "ON" else GPIO.LOW)


def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        # subscribe ทั้งสถานะกล้อง และคำสั่งเปิด/ปิดไฟ
        client.subscribe([(STATUS_TOPIC, 1), (COMMAND_TOPIC, 1)])
        logging.info("MQTT connected")


def on_message(client, userdata, msg):
    global person_status
    payload = msg.payload.decode("utf-8").strip().upper()

    if msg.topic == COMMAND_TOPIC:
        if payload in ("ON", "OFF"):
            apply_led(payload)
            logging.info("LED -> %s (from MQTT)", payload)
        else:
            logging.warning("Ignored unknown command: %r", payload)

    elif msg.topic == STATUS_TOPIC:
        with status_lock:
            person_status = payload


mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

mqtt_client.connect(BROKER, PORT, 60)
mqtt_client.loop_start()

# Create MCP Server
mcp = MCPServer("RaspberryPi-IoT")


@mcp.tool()
def set_led(action: str) -> str:
    """Turn the IoT LED on or off via MQTT.
    action must be exactly 'on' or 'off'.
    """
    action = action.strip().lower()

    if action not in ("on", "off"):
        return "Error: action must be on or off"

    # Publish only an allowed command
    info = mqtt_client.publish(
        COMMAND_TOPIC,
        action.upper(),
        qos=1
    )
    info.wait_for_publish(timeout=5)

    if info.rc != mqtt.MQTT_ERR_SUCCESS:
        return "MQTT publish failed"

    return f"Sent LED command: {action.upper()}"


@mcp.tool()
def set_led_raspi(action: str) -> str:
    """Turn Raspberry Pi LED on or off directly via GPIO."""
    action = action.strip().lower()

    if action == "on":
        apply_led("ON")
        return "LED is ON"

    if action == "off":
        apply_led("OFF")
        return "LED is OFF"

    return "Error: action must be on or off"


@mcp.tool()
def get_person_status() -> str:
    """Get the latest person detection status from the camera."""
    with status_lock:
        status = person_status

    if status is None:
        return (
            "No camera status received yet. "
            "Check that the AI camera publishes to "
            + STATUS_TOPIC
        )

    return f"Latest camera status: {status}"


if __name__ == "__main__":
    # MCP over Streamable HTTP
    security = TransportSecuritySettings(
        allowed_hosts=[
            "clear-river-0b21df56.tunnl.gg",
            "clear-river-0b21df56.tunnl.gg:*",
            "localhost:8000",
            "127.0.0.1:8000",
            "0.0.0.0:8000",
        ],
        allowed_origins=[
            "https://clear-river-0b21df56.tunnl.gg/",
        ],
    )

    try:
        mcp.run(
            transport="streamable-http",
            transport_security=security,
            host="0.0.0.0",
        )
    finally:
        mqtt_client.loop_stop()
        mqtt_client.disconnect()
        GPIO.cleanup()