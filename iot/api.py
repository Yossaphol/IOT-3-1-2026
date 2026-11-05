import json, threading, time
from collections import deque
from contextlib import asynccontextmanager
from typing import Literal

import paho.mqtt.client as mqtt
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

BROKER, PORT = "broker.hivemq.com", 1883
P = "yossaphol-iot-3502"
T_LED_CMD = f"{P}/pi/device/led"
T_LED_STATE = f"{P}/pi/device/led/state"
T_IR = f"{P}/pi/sensor/ir"
T_LORA = f"{P}/lora/node1/data"   # ใช้ในขั้น 5 (ตอนนี้ยังไม่มีข้อมูล)

state = {"led": None, "ir": None, "light": None, "light_raw": None, "dark": None}
updated = {}
events = deque(maxlen=50)
lock = threading.Lock()

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=f"pi-api-{P}")


def on_connect(c, userdata, flags, reason_code, properties):
    c.subscribe([(T_LED_STATE, 1), (T_IR, 1), (T_LORA, 0)])


def on_message(c, userdata, msg):
    payload = msg.payload.decode("utf-8", errors="replace").strip()
    now = time.time()
    with lock:
        if msg.topic == T_LED_STATE:
            state["led"] = payload
            updated["led"] = now
        elif msg.topic == T_IR:
            if payload != state["ir"]:
                events.appendleft({"t": now, "ir": payload})
            state["ir"] = payload
            updated["ir"] = now
        elif msg.topic == T_LORA:
            try:
                d = json.loads(payload)
            except ValueError:
                return
            for k in ("light", "light_raw", "dark"):
                if k in d:
                    state[k] = d[k]
            updated["light"] = now


client.on_connect = on_connect
client.on_message = on_message


@asynccontextmanager
async def lifespan(app):
    client.connect(BROKER, PORT, 60)
    client.loop_start()
    yield
    client.loop_stop()
    client.disconnect()


app = FastAPI(lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


class LedCmd(BaseModel):
    state: Literal["ON", "OFF"]


@app.get("/api/status")
def status():
    with lock:
        return {**state, "updated": dict(updated), "events": list(events)}


@app.post("/api/led")
def set_led(cmd: LedCmd):
    info = client.publish(T_LED_CMD, cmd.state, qos=1)
    info.wait_for_publish(timeout=5)
    if info.rc != mqtt.MQTT_ERR_SUCCESS:
        raise HTTPException(502, "MQTT publish failed")
    return {"sent": cmd.state}