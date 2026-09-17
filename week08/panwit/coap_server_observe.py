import asyncio
from aiocoap import resource, Context, Message
import aiocoap

class TemperatureResource(resource.ObservableResource):

    def __init__(self):
        super().__init__()
        self.temperature = 25.0

    async def render_get(self, request):
        print("GET /temperature")

        return Message(
            code=aiocoap.Code.CONTENT,
            payload=str(self.temperature).encode()
        )

    async def update_temperature(self):

        while True:
            await asyncio.sleep(3)

            # สมมติว่าอ่านค่าจาก Sensor
            self.temperature += 0.5

            print("Temperature =", self.temperature)

            # แจ้ง Client ที่ Observe อยู่
            self.updated_state()


async def main():

    root = resource.Site()

    temperature = TemperatureResource()

    root.add_resource(
        ["temperature"],
        temperature
    )

    await Context.create_server_context(
        root,
        bind=("127.0.0.1", 5683)
    )

    print("CoAP Server started")

    asyncio.create_task(
        temperature.update_temperature()
    )

    await asyncio.get_running_loop().create_future()


asyncio.run(main())