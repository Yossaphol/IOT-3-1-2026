import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BOARD)

red = 36
green = 38
blue = 40

GPIO.setup(red,GPIO.OUT)
GPIO.setup(green,GPIO.OUT)
GPIO.setup(blue,GPIO.OUT)

while True:
	GPIO.output(red,True)
	GPIO.output(green,False)
	GPIO.output(blue,False)
	time.sleep(1)

	GPIO.output(green,True)
	GPIO.output(red,False)
	GPIO.output(blue,False)
	time.sleep(1)

	GPIO.output(blue,True)
	GPIO.output(red,False)
	GPIO.output(green,False)
	time.sleep(1)

	GPIO.output(red,True)
	GPIO.output(green,True)
	GPIO.output(blue,False)
	time.sleep(1)

	GPIO.output(red,True)
	GPIO.output(blue,True)
	GPIO.output(green,False)
	time.sleep(1)

	GPIO.output(green,True)
	GPIO.output(blue,True)
	GPIO.output(red,False)
	time.sleep(1)

	GPIO.output(red,False)
	GPIO.output(green,False)
	GPIO.output(blue,False)
	time.sleep(1)

	GPIO.output(red,True)
	GPIO.output(green,True)
	GPIO.output(blue,True)
	time.sleep(1)