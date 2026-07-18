import spidev
import random
import time
import RPi.GPIO as GPIO

# =============================
# SPI Setup
# =============================

spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 1000000

# =============================
# GPIO Setup
# =============================

GPIO.setmode(GPIO.BOARD)

SW_PIN = 11

GPIO.setup(SW_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# =============================
# Read MCP3208
# =============================

def read_adc(channel):

    command = [
        0x06 | (channel >> 2),
        (channel & 0x03) << 6,
        0
    ]

    adc = spi.xfer2(command)

    value = ((adc[1] & 0x0F) << 8) | adc[2]

    return value


# =============================
# Read Joystick Direction
# =============================

def get_direction():

    x = read_adc(0)
    y = read_adc(1)

    if x < 1000:
        return "LEFT"

    elif x > 3000:
        return "RIGHT"

    elif y < 1000:
        return "UP"

    elif y > 3000:
        return "DOWN"

    return "CENTER"


# =============================
# Game Variables
# =============================

directions = ["LEFT", "RIGHT", "UP", "DOWN"]

score = 0

best_time = None

# =============================
# Start
# =============================

print("======================================")
print("      Reaction Test Game")
print("======================================")
print("Move the joystick in the direction")
print("shown on the screen.")
print("Press the joystick button (SW)")
print("to exit the game.")
print("======================================")

try:

    while True:

        # Exit Game
        if GPIO.input(SW_PIN) == GPIO.LOW:
            print("\nGame End")
            break

        print("\nGet Ready...")

        time.sleep(random.randint(2, 4))

        target = random.choice(directions)

        print(f"\n>>> MOVE {target} <<<")

        start = time.time()

        while True:

            # Exit Game
            if GPIO.input(SW_PIN) == GPIO.LOW:
                print("\nGame End")
                raise KeyboardInterrupt

            direction = get_direction()

            if direction == target:

                end = time.time()

                reaction = end - start

                score += 1

                if best_time is None or reaction < best_time:
                    best_time = reaction

                print("--------------------------------------")
                print("Correct!")
                print(f"Reaction Time : {reaction:.3f} sec")
                print(f"Score         : {score}")
                print(f"Best Time     : {best_time:.3f} sec")
                print("--------------------------------------")

                break

            time.sleep(0.02)

except KeyboardInterrupt:
    pass

finally:

    spi.close()

    GPIO.cleanup()

    print("\n======================================")
    print("Final Score :", score)

    if best_time is not None:
        print(f"Best Time  : {best_time:.3f} sec")

    print("Thank you for playing!")
    print("======================================")