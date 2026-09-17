import asyncio
import aiocoap
import aiocoap.resource as resource
import RPi.GPIO as GPIO

# =========================
# GPIO
# =========================
LED_PIN = 14

GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_PIN, GPIO.OUT)

# PWM 1000 Hz
pwm = GPIO.PWM(LED_PIN, 1000)
pwm.start(0)


# =========================
# CoAP Resource
# =========================
class LEDResource(resource.Resource):
    async def render_put(self, request):
        payload = request.payload.decode().strip()
        print("PUT /led =", payload)

        try:
            brightness = int(payload)
            if brightness < 0 or brightness > 100:
                return aiocoap.Message(
                    code=aiocoap.Code.BAD_REQUEST,
                    payload=b"Value must be between 0 and 100"
                )

            pwm.ChangeDutyCycle(brightness)
            print("LED brightness =", brightness, "%")
            return aiocoap.Message(
                code=aiocoap.Code.CHANGED,
                payload=f"LED brightness = {brightness}%".encode()
            )

        except ValueError:

            return aiocoap.Message(
                code=aiocoap.Code.BAD_REQUEST,
                payload=b"Invalid value"
            )


# =========================
# Main
# =========================
async def main():
    root = resource.Site()
    root.add_resource(
        ["led"],
        LEDResource()
    )

    await aiocoap.Context.create_server_context(
        root,
        bind=("0.0.0.0", 5683)
    )

    print("CoAP Server started")
    print("Resource: coap://172.20.10.2:5683/led")

    await asyncio.get_running_loop().create_future()


if __name__ == "__main__":

    try:
        asyncio.run(main())

    except KeyboardInterrupt:
        print("\nStopping server...")

    finally:
        pwm.stop()
        GPIO.cleanup()