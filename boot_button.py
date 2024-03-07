from main import Jarvis, Shutdown
import RPi.GPIO as GPIO
from pygame import mixer
from time import sleep

jv = Jarvis()

pin = 12
GPIO.setmode(GPIO.BCM)
GPIO.setup(pin, GPIO.IN)

mixer.init()
mixer.music.load('./media/welcome_back.mp3')

try:
    mixer.music.play()
    
    jv.startup()

    print('JARVIS activated')

    while True:
        state = GPIO.input(pin)

        if state:
            jv.run()

except Shutdown:
    mixer.music.load('./media/shutting_down.mp3')
    mixer.music.play()
    sleep(2)

finally:
    GPIO.cleanup()