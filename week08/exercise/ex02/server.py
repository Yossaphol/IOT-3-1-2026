import asyncio
from aiocoap import *
from aiocoap import resource

import RPi.GPIO as GPIO

# =========================
# GPIO Setup
# =========================

LED_PIN = 14

GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_PIN, GPIO.OUT)

pwm = GPIO.PWM(LED_PIN, 1000)
pwm.start(0)


# =========================
# CoAP LED Resource
# =========================

class LEDResource(resource.Resource):

    async def render_put(self, request):

        try:
            value = request.payload.decode().strip()

            brightness = int(value)

            brightness = max(0, min(100, brightness))

            pwm.ChangeDutyCycle(brightness)

            print(f"Received: {brightness}")
            print(f"LED Brightness: {brightness}%")

            return Message(
                code=Code.CHANGED,
                payload=f"LED Brightness: {brightness}%".encode()
            )

        except Exception as e:

            print("Error:", e)

            return Message(
                code=Code.BAD_REQUEST,
                payload=b"Invalid value"
            )


# =========================
# Start CoAP Server
# =========================

async def main():

    root = resource.Site()

    root.add_resource(
        ['led'],
        LEDResource()
    )

    protocol = await Context.create_server_context(
        root,
        bind=('0.0.0.0', 5683)
    )

    print("================================")
    print("CoAP Server Started")
    print("LED GPIO : 14")
    print("Resource : /led")
    print("Port     : 5683")
    print("Waiting for PUT request...")
    print("================================")

    try:
        await asyncio.get_running_loop().create_future()

    except KeyboardInterrupt:
        pass

    finally:
        pwm.stop()
        GPIO.cleanup()


if __name__ == "__main__":
    asyncio.run(main())