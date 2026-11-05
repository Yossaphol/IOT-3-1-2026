import time
from signal import pause

import paho.mqtt.client as mqtt
from gpiozero import LED, Button, DigitalOutputDevice

BROKER = "broker.hivemq.com"
PORT = 1883
P = "yossaphol-iot-3502"          # คำนำหน้า topic กันชนกับคนอื่นบน broker สาธารณะ

T_LED_CMD = f"{P}/pi/device/led"          # รับคำสั่ง: ON / OFF
T_LED_STATE = f"{P}/pi/device/led/state"  # ส่งสถานะจริง: ON / OFF
T_IR = f"{P}/pi/sensor/ir"                # ส่งสถานะ: DETECTED / CLEAR

led = LED(4)                                          # pin 7
en = DigitalOutputDevice(24, initial_value=True)      # IR EN = pin 18
ir = Button(23, pull_up=True, bounce_time=0.02)       # IR OUT = pin 16 (active LOW)

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=f"pi-{P}")


def publish_led():
    client.publish(T_LED_STATE, "ON" if led.is_lit else "OFF", qos=1, retain=True)


def publish_ir():
    client.publish(T_IR, "DETECTED" if ir.is_pressed else "CLEAR", qos=1, retain=True)


def on_connect(c, userdata, flags, reason_code, properties):
    print("MQTT connected:", reason_code)
    c.subscribe(T_LED_CMD, qos=1)
    publish_led()
    publish_ir()


def on_message(c, userdata, msg):
    print("RX:", msg.topic, msg.payload)
    cmd = msg.payload.decode("utf-8", errors="replace").strip().upper()
    if cmd == "ON":
        led.on()
    elif cmd == "OFF":
        led.off()
    else:
        print("ignored command:", repr(cmd))
        return
    print("LED ->", cmd)
    publish_led()


client.on_connect = on_connect
client.on_message = on_message
ir.when_pressed = publish_ir
ir.when_released = publish_ir

client.connect(BROKER, PORT, 60)
client.loop_start()
print("Running... (Ctrl+C เพื่อออก)")
try:
    pause()
except KeyboardInterrupt:
    pass
finally:
    client.loop_stop()
    client.disconnect()