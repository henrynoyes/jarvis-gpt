from main import Jarvis, Shutdown
import RPi.GPIO as GPIO
from pygame import mixer
from time import sleep

jv = Jarvis()

pin = 13
GPIO.setmode(GPIO.BCM)
GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

mixer.init()
mixer.music.load('./media/welcome_back.mp3')

try:
    mixer.music.play()
    
    jv.startup()

    print('JARVIS activated')

    while True:
        state = GPIO.input(pin)
        
        sleep(0.05)
        if state:
            jv.run()
            

except Shutdown:
    mixer.music.load('./media/shutting_down.mp3')
    mixer.music.play()
    sleep(2)

except KeyboardInterrupt:
    pass

finally:
    GPIO.cleanup()
