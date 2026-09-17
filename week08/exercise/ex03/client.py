import asyncio

from aiocoap import Context, Message
import aiocoap

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
# Main
# =========================

async def main():

    protocol = await Context.create_client_context()

    request = Message(
        code=aiocoap.Code.GET,
        uri="coap://172.20.10.4:5683/potentiometer"
    )

    # Start Observe
    request.opt.observe = 0

    requester = protocol.request(request)

    # =========================
    # First Response
    # =========================

    response = await requester.response

    value = int(response.payload.decode())

    brightness = int(value * 100 / 1023)

    pwm.ChangeDutyCycle(brightness)

    print(
        f"Potentiometer: {value} "
        f"Brightness: {brightness}%"
    )


    # =========================
    # Observe Notifications
    # =========================

    async for response in requester.observation:

        value = int(response.payload.decode())

        brightness = int(value * 100 / 1023)

        pwm.ChangeDutyCycle(brightness)

        print(
            f"Potentiometer: {value} "
            f"Brightness: {brightness}%"
        )


# =========================
# Run
# =========================

try:

    asyncio.run(main())

except KeyboardInterrupt:

    pass

finally:

    pwm.stop()
    GPIO.cleanup()