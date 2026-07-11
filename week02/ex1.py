import RPi.GPIO as GPIO
import time

KEYPAD = [
	[1, 2, 3, 'A'],
	[4, 5, 6, 'B'],
	[7, 8, 9, 'C'],
	['*', 0, '#', 'D']
]

ROWS = [7, 11, 13, 15]
COLS = [29, 31, 33, 35]

red = 8
green = 10
blue = 12

GPIO.setmode(GPIO.BOARD)

for row_pin in ROWS:
	GPIO.setup(row_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
for col_pin in COLS:
	GPIO.setup(col_pin, GPIO.OUT)
	GPIO.output(col_pin, GPIO.HIGH)

GPIO.setup(red, GPIO.OUT)
GPIO.setup(green, GPIO.OUT)
GPIO.setup(blue, GPIO.OUT)

def set_color(r, g, b):
	GPIO.output(red, r)
	GPIO.output(green, g)
	GPIO.output(blue, b)

def led_off():
	GPIO.output(red, GPIO.HIGH)
	GPIO.output(green, GPIO.HIGH)
	GPIO.output(blue, GPIO.HIGH)

def get_key():
	key = None
	for col_num, col_pin in enumerate(COLS):
		GPIO.output(col_pin, GPIO.LOW)
		for row_num, row_pin in enumerate(ROWS):
			if GPIO.input(row_pin) == GPIO.LOW:
				key = KEYPAD[row_num][col_num]
				if key == 1: set_color(0, 1, 1)
				elif key == 2: set_color(1, 0, 1)
				elif key == 3: set_color(1, 1, 0)
				elif key == 4: set_color(0, 0, 1)
				elif key == 5: set_color(1, 0, 0)
				elif key == 6: set_color(0, 1, 0)
				elif key == 7: set_color(0, 0, 0)

				while GPIO.input(row_pin) == GPIO.LOW:
					time.sleep(0.02)

				led_off()
		GPIO.output(col_pin, GPIO.HIGH)
	return key

color_map = {
	1: "Red",
	2: "Green",
	3: "Blue",
	4: "Red + Green (Yellow)",
	5: "Green + Blue (Cyan)",
 	6: "Red + Blue (Magenta)",
	 7: "Red + Green + Blue (White)"
}

try:
	led_off()
	while True:
		pressed_key = get_key()
		if pressed_key is not None:
			print(f"Pressed: {pressed_key} -> {color_map.get(pressed_key, 'No Color')}")
		time.sleep(0.05)

except KeyboardInterrupt:
	GPIO.cleanup()