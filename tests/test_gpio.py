import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BOARD)
GPIO.setup(13, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

while True:

	print(GPIO.input(13))
	time.sleep(0.5)
