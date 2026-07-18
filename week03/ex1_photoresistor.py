import RPi.GPIO as GPIO
import time

LED_pin = 18
SENSOR_pin = 16

GPIO.setmode(GPIO.BOARD)

GPIO.setup(LED_pin, GPIO.OUT)
GPIO.setup(SENSOR_pin, GPIO.IN)

try:
	while True:
		sensor_value = GPIO.input(SENSOR_pin)

		if sensor_value == 1:
			GPIO.output(LED_pin, GPIO.LOW)
			print(f"Sensor value: {sensor_value}")
		else:
			GPIO.output(LED_pin, GPIO.HIGH)
			print(f"Sensor value: {sensor_value}")
		time.sleep(0.5)

except KeyboardInterrupt:
	print("\nProgram stopped")

finally:
	GPIO.cleanup()