import base64, json, os, time
import paho.mqtt.client as mqtt

LORA_HOST, LORA_PORT = "lora.kmitl.ac.th", 1883
LORA_USER = os.getenv("LORA_USER")      # ถ้า broker ต้องใช้ username/password
LORA_PASS = os.getenv("LORA_PASS")
HIVE_HOST, HIVE_PORT = "broker.hivemq.com", 1883
P = "yossaphol-iot-3502"
T_OUT = f"{P}/lora/node1/data"

# Device EUI ของเรา (ใส่ทั้ง 2 ลำดับไบต์ไว้ก่อน เพราะยังไม่ได้ยืนยันจากหน้า ChirpStack)
MY_DEVEUIS = {"75a81c9ad28030c1"}

hive = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=f"bridge-hive-{P}")
hive.connect(HIVE_HOST, HIVE_PORT, 60)
hive.loop_start()


def on_connect(c, userdata, flags, reason_code, properties):
    print("ChirpStack MQTT:", reason_code)
    c.subscribe("application/+/device/+/event/up")


def on_message(c, userdata, msg):
    try:
        ev = json.loads(msg.payload)
    except ValueError:
        return
    info = ev.get("deviceInfo", {})
    eui = str(info.get("devEui", "")).lower()
    if os.getenv("DEBUG"):
        print("seen:", eui, info.get("deviceName"))
    if eui not in MY_DEVEUIS:
        return
    try:
        b = base64.b64decode(ev.get("data", ""))
    except ValueError:
        return
    if len(b) < 2:
        return
    raw = (b[0] << 8) | b[1]
    out = {
        "light_raw": raw,
        "light": round((1023 - raw) / 1023 * 100, 1),   # ยิ่งสว่าง ค่ายิ่งมาก
        "ts": int(time.time()),
    }
    if len(b) >= 3:
        out["dark"] = b[2] == 1
    rx = (ev.get("rxInfo") or [{}])[0]
    out["rssi"], out["snr"] = rx.get("rssi"), rx.get("snr")
    hive.publish(T_OUT, json.dumps(out), qos=1, retain=True)
    print("uplink ->", out)


lora = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=f"bridge-lora-{P}")
if LORA_USER:
    lora.username_pw_set(LORA_USER, LORA_PASS)
lora.on_connect = on_connect
lora.on_message = on_message
lora.connect(LORA_HOST, LORA_PORT, 60)
lora.loop_forever()