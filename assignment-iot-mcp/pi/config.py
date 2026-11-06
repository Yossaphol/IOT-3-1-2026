"""ค่าตั้งต้นทั้งหมดของฝั่ง Raspberry Pi (แก้ผ่าน environment variable ได้)

หน้าที่ของ Pi ในระบบนี้: MCP Server + LED (เปิด/ปิด) + Ultrasonic (วัดระยะ)
ค่าความเข้มแสงมาจาก Arduino LoRa node ผ่าน MQTT (topic lora/node1/data)
"""
import os

# ---------- MQTT ----------
MQTT_BROKER = os.getenv("MQTT_BROKER", "mqtt-dashboard.com")   # broker สาธารณะ (HiveMQ) ใช้ Mosquitto ของตัวเองก็ได้
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
MQTT_USER = os.getenv("MQTT_USER")                    # ถ้า broker ไม่มี auth ให้ปล่อยว่าง
MQTT_PASS = os.getenv("MQTT_PASS")

# คำนำหน้าทุก topic กันชนกับคนอื่นบน broker สาธารณะ (เช่น mqtt-dashboard.com)
# ต้องตั้งค่าเดียวกันทุกเครื่อง: Pi, bridge และ API (env TOPIC_PREFIX)
TOPIC_PREFIX = os.getenv("TOPIC_PREFIX", "khaopad-iot-a7f3").strip("/")


def full_topic(short: str) -> str:
    """'pi/device/led' -> 'khaopad-iot-a7f3/pi/device/led'"""
    short = short.strip("/")
    return short if short.startswith(TOPIC_PREFIX + "/") else f"{TOPIC_PREFIX}/{short}"


def short_topic(full: str) -> str:
    """'khaopad-iot-a7f3/pi/device/led' -> 'pi/device/led'"""
    return full[len(TOPIC_PREFIX) + 1:] if full.startswith(TOPIC_PREFIX + "/") else full


TOPIC_DISTANCE = full_topic("pi/sensor/distance")
TOPIC_LED_CMD = full_topic("pi/device/led")          # คำสั่ง: ON / OFF
TOPIC_LED_STATE = full_topic("pi/device/led/state")  # สถานะจริง: ON / OFF
TOPIC_LORA_LIGHT = full_topic("lora/node1/data")     # ค่าแสงจาก Arduino: {"light": 0-100, "light_raw": 0-1023, "dark": bool}

# topic ที่ MCP tool publish_to_mqtt อนุญาตให้เขียนได้ (whitelist)
PUBLISH_WHITELIST = {TOPIC_LED_CMD}

# ---------- GPIO (เลข BCM) ----------
LED_PIN = int(os.getenv("LED_PIN", "4"))      # ขา 7
TRIG_PIN = int(os.getenv("TRIG_PIN", "23"))   # ขา 16
ECHO_PIN = int(os.getenv("ECHO_PIN", "24"))   # ขา 18 (ผ่านตัวต้านทานแบ่งแรงดัน)

PUBLISH_INTERVAL = float(os.getenv("PUBLISH_INTERVAL", "5"))  # วินาที
