import asyncio
from aiocoap import resource, Context, Message
import aiocoap

import RPi.GPIO as GPIO

LIGHT = 17

GPIO.setmode(GPIO.BCM)
GPIO.setup(LIGHT, GPIO.OUT)

class TemperatureResource(resource.Resource):

    async def render_get(self, request):

        print("Method:", request.code)
        print("Payload:", request.payload)

        print("GET /temperature")

        temperature = "25.6"
        return Message(
            code=aiocoap.Code.CONTENT,
            payload=temperature.encode()
        )


class LEDResource(resource.Resource):

    async def render_put(self, request):


        print("Method:", request.code)
        print("Payload:", request.payload)

        command = request.payload.decode()

        print("PUT /led =", command)

        if command == "ON":
            GPIO.output(LIGHT, True)
            print("LED ON")

        elif command == "OFF":
            GPIO.output(LIGHT, False)
            print("LED OFF")

        else:
            return Message(
                code=aiocoap.Code.BAD_REQUEST,
                payload=b"Invalid command"
            )

        return Message(
            code=aiocoap.Code.CHANGED,
            payload=b"OK"
        )


async def main():

    root = resource.Site()

    root.add_resource(
        ["temperature"],
        TemperatureResource()
    )

    root.add_resource(
        ["led"],
        LEDResource()
    )

    await Context.create_server_context(root , bind=("192.168.1.174", 5683))

    print("CoAP Server started")
    print("Port: 5683")

    await asyncio.get_running_loop().create_future()


if __name__ == "__main__":
    asyncio.run(main())