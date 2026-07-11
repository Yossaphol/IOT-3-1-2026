import time
import spidev
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BOARD)

LIGHT = 12

spi = spidev.SpiDev()
spi.open(0,0)
spi.max_speed_hz = 500000

def ReadChannel(channel):
	adc = spi.xfer2([6 | (channel & 4) >> 2, (channel & 3) << 6, 0])
	data = ((adc[1] & 15) << 8) + adc[2]
	return data

GPIO.setup(LIGHT, GPIO.OUT)
pi_pwm = GPIO.PWM(LIGHT,1000)
pi_pwm.start(0)

while True:
	reading = ReadChannel(0)
	voltage = reading * 3.3 / 4096
	print("Reading=%d\t Voltage=%f" % (reading, voltage))

	pi_pwm.ChangeDutyCycle(voltage)

	time.sleep(1)