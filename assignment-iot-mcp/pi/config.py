"""ค่าตั้งต้นทั้งหมดของฝั่ง Raspberry Pi (แก้ผ่าน environment variable ได้)"""
import os

# ---------- MQTT ----------
MQTT_BROKER = os.getenv("MQTT_BROKER", "localhost")   # ตอนทดสอบเปลี่ยนเป็น mqtt-dashboard.com ได้
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
MQTT_USER = os.getenv("MQTT_USER")                    # ถ้า broker ไม่มี auth ให้ปล่อยว่าง
MQTT_PASS = os.getenv("MQTT_PASS")

TOPIC_TEMPERATURE = "pi/sensor/temperature"
TOPIC_HUMIDITY = "pi/sensor/humidity"
TOPIC_DISTANCE = "pi/sensor/distance"
TOPIC_LED_CMD = "pi/device/led"          # คำสั่ง: ON / OFF
TOPIC_LED_STATE = "pi/device/led/state"  # สถานะจริง: ON / OFF

# topic ที่ MCP tool publish_to_mqtt อนุญาตให้เขียนได้ (whitelist)
PUBLISH_WHITELIST = {TOPIC_LED_CMD}

# ---------- GPIO (เลข BCM) ----------
LED_PIN = int(os.getenv("LED_PIN", "4"))
TRIG_PIN = int(os.getenv("TRIG_PIN", "23"))
ECHO_PIN = int(os.getenv("ECHO_PIN", "24"))

# ---------- SHT31 (I2C) ----------
SHT31_ADDR = 0x44

PUBLISH_INTERVAL = float(os.getenv("PUBLISH_INTERVAL", "5"))  # วินาที
