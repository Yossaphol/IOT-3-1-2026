// คัดลอกไปไว้ที่ api/src/routes/devices.ts  แล้วรัน  npm i mqtt
import { Hono } from "hono";
import mqtt from "mqtt";
import { z } from "zod";
import { zValidator } from "@hono/zod-validator";
import { broadcast } from "../ws.js";

const CMD_TOPIC = "pi/device/led";
const STATE_TOPIC = "pi/device/led/state";

const client = mqtt.connect(process.env.MQTT_URL ?? "mqtt://localhost:1883", {
  username: process.env.MQTT_USER,
  password: process.env.MQTT_PASS,
});

let ledState: "ON" | "OFF" | "UNKNOWN" = "UNKNOWN";

client.on("connect", () => client.subscribe(STATE_TOPIC));
client.on("message", (topic, message) => {
  if (topic === STATE_TOPIC) {
    ledState = message.toString() === "ON" ? "ON" : "OFF";
    broadcast({ type: "LED_STATE", data: { state: ledState } });
  }
});

const devicesRouter = new Hono();

devicesRouter.get("/led", (c) => c.json({ state: ledState }));

devicesRouter.post(
  "/led",
  zValidator("json", z.object({ action: z.enum(["on", "off"]) })),
  async (c) => {
    const { action } = c.req.valid("json");
    await client.publishAsync(CMD_TOPIC, action.toUpperCase(), { qos: 1 });
    return c.json({ success: true, sent: action.toUpperCase() });
  }
);

export default devicesRouter;
