# วิธีติดตั้ง devices route

```bash
cd week06/iot-lab-2026/05-sensor-api-with-webapp/api
cp ../../../../assignment-iot-mcp/api-patch/devices.ts src/routes/devices.ts
npm i mqtt
```

แก้ `src/routes/api.ts` 2 จุด:

```ts
import devicesRouter from "./devices.js";          // เพิ่มใต้ import sensorsRouter
...
apiRouter.route("/devices", devicesRouter);        // เพิ่มใต้ apiRouter.route("/sensors", ...)
```

เพิ่มใน `.env`:

```
MQTT_URL=mqtt://localhost:1883
```
