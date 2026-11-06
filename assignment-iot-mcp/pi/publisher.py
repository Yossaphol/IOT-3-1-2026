"""วัดระยะด้วย Ultrasonic ทุก N วินาทีแล้ว publish เข้า MQTT

รัน:  python publisher.py
"""
import time

import paho.mqtt.client as mqtt

import config
import sensors

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="pi-sensor-publisher")
if config.MQTT_USER:
    client.username_pw_set(config.MQTT_USER, config.MQTT_PASS)

client.connect(config.MQTT_BROKER, config.MQTT_PORT, 60)
client.loop_start()
sensors.init_gpio()

print(f"Publishing every {config.PUBLISH_INTERVAL}s to {config.MQTT_BROKER}:{config.MQTT_PORT}")

try:
    while True:
        data = sensors.read_all()
        if data["distance"] is not None:
            client.publish(config.TOPIC_DISTANCE, str(data["distance"]), qos=1)
        print("[PUB]", data)
        time.sleep(config.PUBLISH_INTERVAL)
except KeyboardInterrupt:
    print("\nStopping...")
finally:
    client.loop_stop()
    client.disconnect()
    sensors.cleanup()
