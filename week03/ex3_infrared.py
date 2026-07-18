import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BOARD)

OUT = 16
EN = 18

GPIO.setup(EN, GPIO.OUT)

GPIO.setup(OUT, GPIO.IN)

GPIO.output(EN, GPIO.HIGH)

count = 0
last_state = GPIO.input(OUT)

print("Start...")

try:
    while True:
        state = GPIO.input(OUT)

        if last_state == 1 and state == 0:
            count += 1
            print(f"Detected! Count = {count}")

        last_state = state
        time.sleep(0.02)

except KeyboardInterrupt:
    GPIO.cleanup()