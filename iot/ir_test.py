from gpiozero import Button, DigitalOutputDevice
from signal import pause

en = DigitalOutputDevice(24, initial_value=True)      # EN = pin 18 -> HIGH
ir = Button(23, pull_up=True, bounce_time=0.02)       # OUT = pin 16 (active LOW)

count = 0
def detected():
    global count
    count += 1
    print(f"Detected! Count = {count}")

ir.when_pressed = detected
ir.when_released = lambda: print("Clear")

print("Start...")
pause()